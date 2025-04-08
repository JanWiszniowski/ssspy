
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import extract_delta_t
import event_station_distance
import extract_moment
from adjustText import adjust_text


def fields_amplitudes(R, Delta_t, moment, a, vp, rp_f, rp_i):
    a_ff = np.divide(a/vp, R) * rp_f * moment
    a_fi = np.divide(np.multiply(Delta_t, a), np.square(R)) * rp_i * moment
    return a_ff, a_fi

def fields_on_station(cat, delta_t, m0, amplitudes, rp_i=4, rp_f=1, vp=3900, rho=2700):
    a = 1 / (4 * np.pi * rho * vp * vp)
    keys = list(delta_t.keys())

    amp_diff_all = []
    depth_all = []
    sta_event_dist_all = []
    magnitude_all = []
    station_list = []

    station_colors = {}  # Dictionary to store assigned colors for each station code
    cmap = plt.get_cmap('tab10')
    color_cycle = cmap.colors

    for idx, event in enumerate(cat):
        r = []
        sta = []
        d_t = delta_t.get(keys[idx])
        d_t = dict(sorted(d_t.items()))
        amp = amplitudes.get(keys[idx])
        amp = dict(sorted(amp.items()))
        event_id = event.id
        moment = m0.get(keys[idx])
        print('Fields on stations:', event_id)
        for station in event.stations:
            for key, value in d_t.items():
                if key in station.code:
                    r.append(station.sta_event_distance)
                    sta.append(key)

        R, Delta_t = (r, list(d_t.values()))
        a_ff, a_fi = fields_amplitudes(R, Delta_t, moment, a, vp, rp_f, rp_i)
        perc_ff = np.divide(a_ff * 100, a_ff + a_fi)
        perc_fi = np.divide(a_fi * 100, a_ff + a_fi)

        fname = event_id[-8:] + ".txt"
        with open(fname, "w") as f:
            for (id, code, n_ff, n_fi, p_ff, p_fi, r_amp) in zip(event_id, sta, a_ff, a_fi, perc_ff, perc_fi, amp.values()):
                f.write("{0},{1},{2},{3},{4},{5},{6}\n".format(id, code, n_ff, n_fi, p_ff, p_fi, r_amp))

        # Data for scatter plot for event depth and amplitude difference
        depth = event.location[2]
        amp_diff = [np.abs(calc_amp - meas_amp) for calc_amp, meas_amp in zip(a_ff + a_fi, amp.values())]
        
        depth_all.extend([depth] * len(sta))
        amp_diff_all.extend(amp_diff)
        sta_event_dist_all.extend(R)
        magnitude = (2/3) * np.log10(moment) - 6.07
        magnitude_all.extend([magnitude] * len(sta))
        station_list.extend(sta)

        # Colors for stations
        for i, station_code in enumerate(sta):
            if station_code not in station_colors:
                station_colors[station_code] = color_cycle[i % len(color_cycle)]


    fig1, (ax3, ax4, ax5) = plt.subplots(3, 1, figsize=(10, 15))

    # Plot each station with its assigned color
    for station_code, depth, amp_diff, mag, dist in zip(station_list, depth_all, amp_diff_all, magnitude_all, sta_event_dist_all):
        color = station_colors[station_code]
        ax3.scatter(depth, amp_diff, color=color, label=station_code, marker='o')
        ax4.scatter(mag, amp_diff, color=color, label=station_code, marker='o')
        ax5.scatter(dist, amp_diff, color=color, label=station_code, marker='o')

    # Create a color legend
    handles, labels = ax3.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    fig1.legend(by_label.values(), by_label.keys(), title='Station Code', loc='upper right')

    ax3.set(xlabel='Depth [m]', ylabel='Amplitude differences [m]')
    ax3.set_xscale("log")
    ax3.set_yscale("log")

    ax4.set(xlabel='Mw', ylabel='Amplitude differences [m]')
    ax4.set_yscale("log")

    ax5.set(xlabel='Event-station distance [m]', ylabel='Amplitude differences [m]')
    ax5.set_xscale("log")
    ax5.set_yscale("log")

    plt.show()
    input("Press enter")

# Example usage
#quakeml_file = 'dane\LGCD_zbiorcze.xml'
quakeml_file = 'dane\STH\STH2_corrected2.xml'
directory = 'dane\dataless_STH'
network_code = 'VN'


def main(quakeml_file, directory, network_code):
    delta_t, amplitudes = extract_delta_t.main(quakeml_file)
    cat = event_station_distance.main(quakeml_file, directory, network_code)
    m0 = extract_moment.main(quakeml_file)
    fields_on_station(cat, delta_t, m0, amplitudes)

main(quakeml_file, directory, network_code)
