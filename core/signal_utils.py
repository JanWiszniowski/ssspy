"""
The waveform and inventory manipulation
---------------------------------------

:copyright:
    Jan Wiszniowski (jwisz@igf.edu.pl)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
:version 0.0.1:
    2025-01-15
"""

import os
import json
import uuid
from abc import ABC, abstractmethod
import core.arclink_client
import obspy.clients.fdsn.client as fdsnws
from obspy import read
from obspy.core.util.obspy_types import ObsPyException
from obspy.core.inventory.inventory import read_inventory
from obspy.core.utcdatetime import UTCDateTime
from obspy.core.stream import Stream


class SignalException(Exception):
    def __init__(self, message="other"):
        self.message = "Signal error: " + message
        super().__init__(self.message)


class StreamPreprocessing(ABC):
    """
    The base class of streams preprocessing

    :param name: The name of the preprocessing
    :type name: str
    """
    def __init__(self, name):
        """
        :param name: The name of the preprocessing
        :type name: str
        """
        self.name = name

    @abstractmethod
    def _process(self, stream):
        """
        Pure method must be overwritten.

        :param stream:
        :type stream:
        :return: None
        """
        pass

    def __call__(self, stream):
        """
        Processing execution

        :param stream:
        :type stream:
        :return: None

        """
        self._process(stream)


class StreamLoader(object):
    """
    The stream loader loads seismic waveforms from servers ArcLink or FDSNWS
    and process data initially. The loaded and processed data can be kept on local disc
    in the cache directory for increase the reloading speed.

    :param configuration: The container of general seismic processing configuration.
        The required parameters are kept in the 'stream' sub-dictionary:
    :type configuration: dict
    :param preprocess:
    :type preprocess: StreamPreprocessing

    **The parameters present in the 'stream' sub-dictionary:**

    :source: The waveforms source. Available options are 'arclink' or 'fdsnws' (required)
    :host: The server host
    :port: The server port
    :user: The request user id (if required)
    :password: The request password (if required)
    :timeout: The downloading timeout limit
    :net: The default network name.
    :sta: The default station name.
    :loc: The default location name.
    :chan: The default channel name.
    :cache: The cache directory. In the cache directory are kept all downloaded and preprocessed waveform files
        and the file 'loaded_signals.json' containing info
    :stations: The default request station list

    """

    def __init__(self, configuration, preprocess=None):
        """
        :param configuration: The container of general seismic processing configuration.
            The required parameters are kept in the 'stream' sub-dictionary:
        :type configuration: dict
        :param preprocess:
        :type preprocess: StreamPreprocessing

        """
        self.stations = None
        self.preprocess = preprocess
        self.stream_source = configuration.get('stream', configuration)
        self.cache = Cache(self.stream_source, 'loaded_signals.json')
        if self.stream_source['source'] == 'arclink':
            self._download_source = self._download_arclink
        elif self.stream_source['source'] == 'fdsnws':
            self._download_source = self._download_fdsnws
        else:
            raise 'Wrong stream source definition'
        self.default_stations = configuration.get('stations')

    def download(self, begin_time, end_time, event_id, new_file_name=None):
        r"""
        Downloads the stream from the seismic data sever with optional caching.

        :param new_file_name: The proposed name of the file tobe stored in the cache.
            If it is missing the unique random name is generated.
        :type new_file_name: str
        :param begin_time: The begin time of waveforms
        :type begin_time: ObsPy.UTCDateTime
        :param end_time: The end time of waveforms
        :type end_time: ObsPy.UTCDateTime
        :param event_id: The event id, but it can be any string defining the stream request,
            which can identify the data in case of repeated inquiry.
        :type event_id: str
        :return: The requested stream or None if it can not be downloaded
        :rtype: ObsPy.Stream

        """
        stream = self._download_source(begin_time, end_time)
        if not stream:
            return 'none'
        preprocess_name = 'none'
        if self.preprocess:
            self.preprocess(stream)
            preprocess_name = self.preprocess.name
        processing = {}
        for trace in stream:
            processing[trace.id] = trace.stats.processing
        if self.cache and event_id:
            if not new_file_name:
                new_file_name = uuid.uuid4()
            file_name = '{}/{}.msd'.format(self.cache.cache_path, new_file_name)
            stream.write(file_name, format='MSEED')
            stream_parameters = {'source': self.stream_source,
                                 'stations': self.stations,
                                 'begin_time': begin_time.isoformat(),
                                 'end_time': end_time.isoformat(),
                                 'file_name': file_name,
                                 'preprocess_name': preprocess_name,
                                 'processing': processing}
            self.cache.loaded_signals[event_id] = stream_parameters
            self.cache.backup()

        return stream

    def _download_arclink(self, begin_time, end_time):
        client = core.arclink_client.Client(host=self.stream_source['host'],
                                            port=self.stream_source.get('port', 18001),
                                            user=self.stream_source['user'],
                                            timeout=self.stream_source.get('timeout', 150))
        signal = Stream()
        for station in self.stations:
            stream = station.split('.')
            stream_format = len(stream)
            try:
                if stream_format == 1:
                    signal += client.get_waveforms(self.stream_source['net'], stream[0],
                                                   self.stream_source.get('loc', ''),
                                                   self.stream_source.get('chan', '*'), begin_time, end_time)
                elif stream_format == 2:
                    signal += client.get_waveforms(stream[0], stream[1],
                                                   self.stream_source.get('loc', ''),
                                                   self.stream_source.get('chan', '*'), begin_time, end_time)
                elif stream_format == 4:
                    signal += client.get_waveforms(stream[0], stream[1], stream[3], stream[4],
                                                   begin_time, end_time)
                else:
                    print('Parameters error: wrong station_name definition {}'.format(station))
            except core.arclink_client.ArcLinkException as e:
                print('ArcLink error: {} reading station_name {}'.format(e.args, station))
        return signal

    def _download_fdsnws(self, begin_time, end_time):
        client = fdsnws.Client(base_url=self.stream_source['host'],
                               user=self.stream_source['user'],
                               timeout=self.stream_source.get('timeout', 300))
        signal = Stream()
        for station in self.stations:
            stream = station.split('.')
            stream_format = len(stream)
            try:
                if stream_format == 1:
                    signal += client.get_waveforms(self.stream_source['net'], stream[0],
                                                   self.stream_source.get('loc', ''),
                                                   self.stream_source.get('chan', '*'), begin_time, end_time)
                elif stream_format == 2:
                    signal += client.get_waveforms(stream[0], stream[1],
                                                   self.stream_source.get('loc', ''),
                                                   self.stream_source.get('chan', '*'), begin_time, end_time)
                elif stream_format == 4:
                    signal += client.get_waveforms(stream[0], stream[1], stream[3], stream[4],
                                                   begin_time, end_time)
                else:
                    print('Parameters error: wrong station_name definition {}'.format(station))
            except fdsnws.FDSNException as e:
                print('FDSNWS error: {} reading station_name {}'.format(e.args, station))
                return None
        return signal

    def exist_file(self, begin_time, end_time, event_id):
        """
        The method checks if the requested waveform exists. A few conditions are checked.
        First it checks if the cache exists. Then checks if event id exists.
        The requested period must include in the existing file period.
        The requested station list must include in the existing file station list.
        The preprocessor name must be the same.

        :param begin_time: The requested waveforms begin time
        :type begin_time: ObsPy.UTCDateTime
        :param end_time: The requested waveforms begin time
        :type end_time: ObsPy.UTCDateTime
        :param event_id: The request event id. It can be the event id that the waveforms are associated
            or any string that identify the request.
        :type event_id: str
        :return: The parameters of existed file or None,
            if the function can not fit request to existing files list
        :rtype: dict

        """
        if not self.cache:
            return None
        if not event_id:
            return None
        loaded_signal = self.cache.loaded_signals.get(event_id)
        if not loaded_signal:
            return None
        if begin_time < UTCDateTime(loaded_signal['begin_time']):
            return None
        if end_time > UTCDateTime(loaded_signal['end_time']):
            return None
        if self.stream_source != loaded_signal['source']:
            return None
        if self.preprocess is None:
            if loaded_signal['preprocess_name'] != 'none':
                return None
        else:
            if loaded_signal['preprocess_name'] != self.preprocess.name:  # self.preprocess.__class__.__name__
                return None
        for station in self.stations:
            if station not in loaded_signal['stations']:
                return None
        return loaded_signal

    def get_signal(self, begin_time, end_time, event_id=None, stations=None, new_file_name=None):
        """
        Provides seismic signal waveform based on request.
        If matching the request file exist in the cache it reads signal from the file,
        otherwise download from the seismic waveforms' server.

        :param begin_time: The requested waveforms begin time
        :type begin_time: ObsPy.UTCDateTime
        :param end_time: The requested waveforms begin time
        :type end_time: ObsPy.UTCDateTime
        :param event_id: The request event id. It can be the event id that the waveforms are associated
            or any string that identify the request. (optional If missing waveform is only downloaded from the server)
        :type event_id: str
        :param stations: The request stations list.
            (optional) If it is missing the station list from the configuration is checked.
        :type stations: list(str)
        :param new_file_name: The name of a file in the cache.
            (optional) If missing the unique file name is generated.
        :type new_file_name: str
        :return: The waveform stream. Return None if it can not (or could not) download waveforms.
        :rtype: ObsPy.Stream

        """
        if stations is None:
            self.stations = self.default_stations
        else:
            self.stations = stations
        loaded_signal = self.exist_file(begin_time, end_time, event_id)
        if loaded_signal:
            if loaded_signal['file_name'] == 'none':
                return None
            stream = read(loaded_signal['file_name'])
            for trace in stream:
                trace.stats.processing = loaded_signal['processing'][trace.id]
            return stream
        stream = self.download(begin_time, end_time, event_id, new_file_name)
        return stream


def load_inventory(configuration):
    """
    Loads inventory from the file. The file name and format are in 'inventory' configuration.
    If inventory file is missing the inventory is downloaded from the waveform server,
    which configuration is in the 'stream' sub-dictionary.

    :param configuration: The container of general seismic processing configuration.
        The required parameters are kept in the 'inventory' sub-dictionary.
    :type configuration: dict
    :return: The inventory
    :rtype: ObsPy.Inventory

    **The parameters present in the 'inventory' sub-dictionary:**

    :file_name: The inventory file name. (optional, default is 'inventory.xml')
    :file_format: The format of the inventory file name. (optional, default is 'STATIONXML')

    """
    inventory_configuration = configuration.get('inventory', configuration)
    file_name = inventory_configuration.get('file_name', 'inventory.xml')
    file_format = inventory_configuration.get('file_format', 'STATIONXML')
    if os.path.exists(file_name) and os.path.isfile(file_name):
        try:
            inventory = read_inventory(file_name, format=file_format)
            return inventory
        except ObsPyException as e:
            print('{} error: {}'.format(file_name, e))

    stream_source = configuration['stream']
    if stream_source['source'] == 'arclink':
        client = core.arclink_client.Client(host=stream_source['host'],
                                            port=stream_source.get('port', 18001),
                                            user=stream_source['user'],
                                            timeout=stream_source.get('timeout', 150))
        client.save_response('temporary.dataless', stream_source.get('net', '*'), stream_source.get('sta', '*'),
                             '.', '*', UTCDateTime(1970, 1, 1, 0, 0), UTCDateTime(2060, 1, 1, 0, 0), format="SEED")
        inventory = read_inventory('temporary.dataless', format='SEED')
        inventory.write(file_name, format=file_format)
        return inventory
    elif stream_source['source'] == 'fdsnws':
        client = fdsnws.Client(base_url=stream_source['host'], user=stream_source['user'],
                               timeout=stream_source.get('timeout', 300))
        inventory = client.get_stations(network=stream_source.get('net'), sta=stream_source.get('sta'),
                                        level="response")
        inventory.write(file_name, format=file_format)
        return inventory
    else:
        raise SignalException('Wrong inventory source definition')


def get_inventory(sta_name, date, inventory):
    """
    Extracts inventory for the station.

    :param sta_name: The station name as the string in the form 'NN.SSS',
        where 'NN' is the network code and 'SSS' is the station code.
    :type sta_name: str
    :param date: The date of the inventory
    :type date: ObsPy.UTCDateTime
    :param inventory: The inventory of all stations
    :type inventory: ObsPy.Inventory
    :return: The inventory of the station
    :rtype: ObsPy.Inventory

    """
    net_code, sta_code = sta_name.split('.', 2)
    for net in inventory.networks:
        if net.code == net_code:
            for sta in net.stations:
                if sta.code == sta_code:
                    if sta.start_date and sta.start_date > date:
                        continue
                    if sta.end_date and sta.end_date < date:
                        continue
                    return sta
    return None


class Cache(object):
    """
    The cache class for manipulating the cache metadata


    :param configuration: The container of general seismic processing configuration.
        The required parameter is a cache path kept in the 'cache'.
    :type configuration: dict
    :param file_name: The cache metadata file name
    :type file_name: str
    """
    def __init__(self, configuration, file_name):
        """

        :param configuration: The container of general seismic processing configuration.
            The required parameter is a cache path kept in the 'cache'.
        :param file_name: The cache metadata file name
        :type file_name: str
        """
        self.loaded_signals = {}
        self.file_name = None
        self.cache_path = configuration.get('cache')
        if self.cache_path is not None and os.path.exists(self.cache_path):
            self.file_name = '{}/{}'.format(self.cache_path, file_name)
            if os.path.exists(self.file_name) and os.path.isfile(self.file_name):
                try:
                    with open(self.file_name, "r") as f:
                        self.loaded_signals = json.load(f)
                except json.JSONDecodeError as e:
                    print(f'{self.file_name}: Invalid JSON syntax - {e}')

    def backup(self):
        """
        Backs up the cache metadata. Saves to the JSON file.

        :return: None

        """
        if self.cache_path:
            with open(self.file_name, "wt") as f:
                json.dump(self.loaded_signals, f, indent=4)

    def __bool__(self):
        return self.file_name is not None
