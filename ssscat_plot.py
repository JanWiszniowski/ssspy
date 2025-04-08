"""
Plot tests for the real catalog
-------------------------------

:copyright:
    Anna Tymińska (atyminska@igf.edu.pl)
    Jan Wiszniowski (jwisz@igf.edu.pl)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
:version 0.0.1:
    2025-02-07

The script facilitates a visual comparison of the behavior of far and intermediate fields for defined stations.
The script utilizes numerical methods and visualization tools provided by the NumPy and Matplotlib
libraries in Python. The script generates numerical simulations for distances (r) and time intervals
(delta_t) defined from each station.
It computes the far field (ff) and intermediate field (fi) behaviors based on specified parameters
and radiation pattern coefficients.
The visualization is facilitated through two sets of plots: 3D visualization
and set of 2D log-log plots.

:call: *python ssspy.py config.json catalog.xml*, where *config.json* is a configuration file
    (see :ref:`configuration`) and *catalog.xml* is a catalog file in QuakeML.

"""

import numpy as np
import matplotlib.pyplot as plt
from utils import extract_amplitude_delta, extract_station_inventories, get_median_rupture_time
from core.utils import get_focal_mechanism, get_origin, get_hypocentral_distance, get_magnitude
from ssspy import time_simulate


def fields_on_station(configuration, catalog):
    """
    **Description required here**

    :param configuration: The configuration container of all parameters dictionary required for the program to work.
    :type configuration: dict
    :param catalog: The events catalog
    :type catalog: ObsPy.Catalog

    """
    stations = extract_station_inventories(configuration)
    color_map = plt.get_cmap('tab10')
    station_colors = {}  # Dictionary to store assigned colors for each station code
    width = 0.5
    for idx, station_codes in enumerate(stations.keys()):
        station_colors[station_codes] = color_map(idx % color_map.N)
    results = []
    ax0 = None
    # fig0, ax0 = plt.subplots()
    for idx, event in enumerate(catalog.events):
        origin = get_origin(event)
        # if idx != 3:
        #     continue
        if origin is None:
            continue
        fm = get_focal_mechanism(event, inversion_type=configuration.get('inversion_type', 'general'))
        if fm is None:
            continue
        scalar_moment = fm.moment_tensor.scalar_moment
        event_id = event.resource_id.id
        print(f'Fields of event {event_id} on stations:', event_id)
        rupture_time = get_median_rupture_time(event)
        if rupture_time is None:
            continue
        for station, station_inventory in stations.items():
            amp, r_t = extract_amplitude_delta(event, station)
            if r_t is None or amp is None:
                continue
            # station_magnitude = extract_station_magnitude(event, station, magnitude_type='Mw')
            # if station_magnitude is None:
            #     continue
            # scalar_moment = 10 ** ((station_magnitude.mag * 1.5) + 9.1)
            source_parameters = {'moment_scalar': scalar_moment, 'rupture_time': rupture_time}
            distance = get_hypocentral_distance(origin, station_inventory)
            # configuration['radial_radiation'] = 0.52  # Setup
            # configuration['density'] = 2700  # Setup
            max_t, max_all, max_near, max_int, max_far = time_simulate(configuration, distance[0], source_parameters,
                                                                       ax=ax0)
            results.append({'event_id': event_id, 'station': station, 'max_all': max_all, 'max_far': max_far,
                            'max_int': max_int, 'max_near': max_near,
                            'perc_far': 100 * max_far / max_all, 'perc_int': 100 * max_int / max_all,
                            'perc_near': 100 * max_near / max_all, 'amplitude': amp, 'rupture_time': rupture_time,
                            'depth': origin.depth, 'distance': distance, 'scalar_moment': scalar_moment})
        # plt.show(block=True)
        # bar plots for each event
        fig, ax = plt.subplots()
        for i, res in enumerate(results):
            if event_id == res['event_id']:
                ax.bar(res['station'], res['max_far'], width, 
                       label='Far field'if i == 0 else "_no_legend_", color='darkred')
                ax.bar(res['station'], res['max_int'], width, bottom=res['max_far'], 
                       label='Intermediate field'if i == 0 else "_no_legend_", color='sandybrown')
                ax.bar(res['station'], res['max_near'], width, bottom=res['max_int']+res['max_far'], 
                       label='Near field'if i == 0 else "_no_legend_", color='gold')
                ax.text(res['station'], 0, f"{res['distance'][0] / 1000:.1f}km", rotation='vertical')
                # ax.scatter(res['station'], res['amplitude'], color='black',
                #            label='Measured amplitude'if i == 0 else "_no_legend_")
        title = f'Fields participation in displacement on stations\n' \
                f'{origin.time.date}, M={get_magnitude(event).mag:.1f}'
        ax.set(ylabel='U[m]', title=title)
        ax.tick_params(axis='x', rotation=55)
        ax.legend()
        mng = plt.get_current_fig_manager()
        # mng.resize(*mng.window.maxsize())
        figtitle = event_id[15:]
        # fig.show()
        plt.savefig(figtitle + '_fields.png')
        plt.close()

    with open(configuration.get('output_file', 'out.txt'), "w") as file:
        for result in results:
            file.write(f"{result['event_id']}, {result['station']}, {result['max_all']}, {result['max_far']}, "
                       f"{result['max_int']}, {result['max_near']}, {result['perc_far']}, {result['perc_int']}, "
                       f"{result['perc_near']}, {result['amplitude']}, {result['rupture_time']}\n")

    # fig1, (ax3, ax4, ax5) = plt.subplots(3, 1, figsize=(10, 15))
    # amplitude_differences = [np.abs(result['max_all'] - result['amplitude']) for result in results]
    # rel_amplitude_differences = [np.abs(result['max_all'] - result['amplitude'])/result['amplitude']
    #                              for result in results]
    # depths = [result['depth'] for result in results]
    # distances = [result['distance'] for result in results]
    # station_codes = [result['station'] for result in results]
    # colors = [station_colors[station_code] for station_code in station_codes]
    # magnitudes = [2 / 3 * np.log10(result['scalar_moment']) - 6.07 for result in results]
    # ax3.scatter(depths, amplitude_differences, color=colors, label=station_codes, marker='o')
    # ax4.scatter(magnitudes, amplitude_differences, color=colors, label=station_codes, marker='o')
    # # ax5.scatter([j[0] for j in distances], amplitude_differences, color=colors, label=station_codes, marker='o')
    # # ax5.scatter([j[0] for j in distances], rel_amplitude_differences, color=colors, label=station_codes, marker='o')
    # ax5.plot([j[0] for j in distances], [result['max_all'] for result in results], 'r.')
    # ax5.plot([j[0] for j in distances], [result['amplitude'] for result in results], 'b.')

    # # Create a color legend
    # handles, labels = ax3.get_legend_handles_labels()
    # by_label = dict(zip(labels, handles))
    # fig1.legend(by_label.values(), by_label.keys(), title='Station Code', loc='upper right')
    #
    # ax3.set(xlabel='Depth [m]', ylabel='Amplitude differences [m]')
    # # ax3.set_xscale("log")
    # # ax3.set_yscale("log")
    #
    # ax4.set(xlabel='Mw', ylabel='Amplitude differences [m]')
    # ax4.set_yscale("log")
    #
    # ax5.set(xlabel='Event-station distance [m]', ylabel='Amplitude differences [m]')
    # # ax5.set_xscale("log")
    # ax5.set_yscale("log")
    #
    # plt.show()
    # input("Press enter")


if __name__ == '__main__':
    from obspy import read_events
    import sys
    import json

    if len(sys.argv) < 3:
        print('call: python ssspy.py config.json catalog.xml')
        sys.exit()
    with open(sys.argv[1], "r") as f:
        Configuration = json.load(f)
    Catalog = read_events(sys.argv[2], format="QUAKEML")
    print(f'{len(Catalog.events)} events in the catalog')
    fields_on_station(Configuration, Catalog)
