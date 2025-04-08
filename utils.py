"""
Utils for simple seismic simulation
-----------------------------------

:copyright:
    Jan Wiszniowski (jwisz@igf.edu.pl)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
:version 0.0.1:
    2025-02-07
"""
import numpy as np
from core.utils import get_origin, get_hypocentral_distance
from core.signal_utils import load_inventory


class SSSException(Exception):
    """
    The simple seismic signal simulation exception class
    """
    def __init__(self, message="other"):
        self.message = "SSSS error: " + message
        super().__init__(self.message)


def extract_station_magnitude(event, station_code, magnitude_type=None):
    for station_magnitude in event.station_magnitudes:
        if station_magnitude.waveform_id.station_code == station_code:
            if magnitude_type is None or station_magnitude.station_magnitude_type and \
                    station_magnitude.station_magnitude_type == magnitude_type:
                return station_magnitude
    return None


def extract_amplitude_delta(event, station_code):
    """
    Function extracting from the event parameters
    displacement amplitude and amplitude duration,
    which is treated as the event rupture time,
    of the station first peak amplitude with mechanism data.

    :param event: The event object
    :type event: ObsPy.Event
    :param station_code: The station code
    :type station_code: (str)
    :return: The displacement amplitude and its duration
    :rtype: tuple(float, float)
    """
    displacement_amplitude = None
    delta = None
    if not event.focal_mechanisms:
        return delta, displacement_amplitude
    for amplitude in event.amplitudes:
        if not amplitude.type or amplitude.type != 'AFPMT':
            continue
        if amplitude.waveform_id.station_code != station_code:
            continue
        if amplitude.unit and amplitude.unit != 'm':
            continue
        channel_code = amplitude.waveform_id.channel_code
        if channel_code.endswith('L') or channel_code.endswith('Z'):
            displacement_amplitude = abs(amplitude.generic_amplitude)
            if amplitude.time_window:
                delta = amplitude.time_window.end + amplitude.time_window.begin
            break
    return displacement_amplitude, delta


def calculate_distance(event, station_inventory):
    origin = get_origin(event)
    distance, _ = get_hypocentral_distance(origin, station_inventory)
    return distance


def extract_station_inventories(configuration):
    inventory = load_inventory(configuration)
    station_inventories = {}
    for network in inventory:
        for station in network:
            station_inventories[station.code] = station
    return station_inventories


def get_median_rupture_time(event):
    if not event.focal_mechanisms:
        return None
    rupture_times = []
    for amplitude in event.amplitudes:
        if not amplitude.type or amplitude.type != 'AFPMT':
            continue
        if amplitude.unit and amplitude.unit != 'm':
            continue
        channel_code = amplitude.waveform_id.channel_code
        if channel_code.endswith('L') or channel_code.endswith('Z'):
            if amplitude.time_window:
                rupture_times.append(amplitude.time_window.end + amplitude.time_window.begin)
    if not rupture_times:
        return None
    return np.median(np.array(rupture_times))
