"""
The script facilitates a visual comparison of the behavior of far and intermediate fields for defined stations. 
The script utilizes numerical methods and visualization tools provided by the NumPy and Matplotlib 
libraries in Python. The script generates numerical simulations for distances (r) and time intervals 
(delta_t) dafined form each station. It computes the far field (ff) and intermediate field (fi) behaviors based on specified parameters 
and radiation pattern coefficients. The visualization is facilitated through two sets of plots: 3D visualization 
and set of 2D log-log plots.

Parameters:
rho- density of the rock medium in the source. Default value 2700 kg/m^3.
vp- P-wave velocity [m/s]. Default value 3720 m/s.
r- event-station distance
delta_t-  time of the first P-wave peak duration/time width of the first P-wave peak [s].
rp_i- radiation pattern coeficient for intermediate field. Default set to 4.
rp_f- radiation pattern coeficient for far field. Default set to 1.




(Aki, Richards)
(Mendecki,1997, Seismic monitoring in mines)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import extract_delta_t
import event_station_distance
import extract_moment
from adjustText import adjust_text
from sklearn.linear_model import LinearRegression



def fields_amplitudes(R, Delta_t,moment, a, vp, rp_f, rp_i):
    a_ff = np.divide(a/vp, R) * rp_f * moment
    a_fi = np.divide(np.multiply(Delta_t, a), np.square(R)) * rp_i * moment
    return a_ff, a_fi

def fields_on_station( cat, delta_t, m0, amplitudes,rp_i = 4, rp_f = 1, vp = 5900, rho = 2700):

    a = 1/(4*np.pi*rho*vp*vp)
    keys = list(delta_t.keys())
    amp_diff_all = []
    depth_all = []
    sta_event_dist_all = []
    station_colors = {}
    magnitude_all = []
    station_list = []
    fig1,(ax3, ax4, ax5) = plt.subplots(3,1,sharey=True, layout='constrained')

    for idx,event in enumerate(cat):
        r = []
        sta = []
        d_t = delta_t.get(keys[idx])
        d_t = dict(sorted(d_t.items()))
        amp = amplitudes.get(keys[idx])
        amp = dict(sorted(amp.items()))
        event_id = event.id
        moment = m0.get(keys[idx])
        print('Fields on stations:',event_id)
        for station in event.stations:
            for key,value in d_t.items():
                if key in station.code:
                    r.append(station.sta_event_distance)
                    sta.append(key)
        
        
        R, Delta_t = (r, list(d_t.values()))
        a_ff, a_fi = fields_amplitudes(R, Delta_t, moment, a, vp, rp_f, rp_i)
        perc_ff = np.divide(a_ff*100,a_ff+a_fi)
        perc_fi = np.divide(a_fi*100,a_ff+a_fi)



        # save txt file
        fname = event_id[-8:]+".txt"
        with open(fname,"w") as f:
            for (id, code, n_ff, n_fi, p_ff, p_fi, r_amp) in zip(event_id, sta, a_ff, a_fi, perc_ff, perc_fi, amp.values()):
                f.write("{0},{1},{2},{3},{4},{5},{6}\n".format(id, code,n_ff, n_fi, p_ff, p_fi, r_amp))

        #bar plot with far and intermediate field amplitudes and dot-measured amplitudes
        fig2,ax = plt.subplots()
        width = 0.5
        ax.bar(sta, a_ff, width, label='Far field')
        ax.bar(sta, a_fi, width, bottom=a_ff, label='Intermediate field')
        ax.scatter(sta, amp.values(),color='black', label='Measured amplitude')
        ax.set(ylabel = 'U[m]',title = 'Intermediate and far field participation in displacement on stations')
        ax.tick_params(axis='x', rotation=55)
        ax.legend()
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        figtitle = event_id[-8:]
        plt.savefig(figtitle + '_sta.png')
        plt.close()

        # scatter plots with comparison of measured and calculated amplitudes
        fig3,(ax1, ax2) = plt.subplots(1,2,sharex="all")
        ax1.scatter(a_ff, amp.values())
        labels1 = [ax1.annotate(f"{i}", (j, amp.get(i)), ha='center') for i, j in zip(amp.keys(), a_ff)]
        ax1.set(ylabel='Measured amplitudes [m]', xlabel='Calculated far field amplitudes [m]')
        ax2.scatter(a_ff + a_fi, amp.values())
        labels2 = [ax2.annotate(f"{i}", (j, amp.get(i)), ha='center') for i, j in zip(amp.keys(), a_ff + a_fi)]
        ax2.set(ylabel='Measured amplitudes [m]', xlabel='Calculated total amplitudes [m]')
        adjust_text(labels1, ax=ax1, arrowprops=dict(arrowstyle="->", color='k', lw=0.8),min_arrow_len=8)
        adjust_text(labels2, ax=ax2, arrowprops=dict(arrowstyle="->", color='k', lw=0.8),min_arrow_len=8)
        ax2.set(ylabel = 'Measured amplitudes [m]', xlabel = 'Calculated total amplitudes [m]')
        plt.suptitle('Comparision of measured and calculated amplitudes')
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        plt.savefig(figtitle +'_amp.png')
        #plt.show()
        plt.close()

        # data for scatter plot for event depth and amplitude difference
        depth = event.location[2]
        amp_diff = [calc_amp - meas_amp for calc_amp, meas_amp in zip(a_ff + a_fi, amp.values())]
        amp_diff_all.extend(amp_diff)
        depth_all.extend([depth] * len(amp))
        sta_event_dist = [station.sta_event_distance for station.code in event.stations]
        sta_event_dist_all.extend(sta_event_dist)
        mag=(2/3)*np.log10(moment)-6.07
        magnitude_all.extend([mag] * len(amp))
        station_list.extend(sta)

        
        #colors for stations
        for i, station_code in enumerate(sta):
            if station_code not in station_colors:
                station_colors[station_code] = plt.cm.tab10(i % 10)
        
        

        # Plot each station with its assigned color
        for station_code, amp_diff_station in zip(sta,amp_diff):
            color = station_colors[station_code]
            ax3.scatter(depth, amp_diff_station, color=color, label=station_code,marker='o')

        for station_code, amp_diff_station in zip(sta, amp_diff):
            color = station_colors[station_code]
            ax4.scatter(mag, amp_diff_station, color=color, label=station_code,marker='o')

        for station_code, amp_diff_station,dist in zip(sta, amp_diff,R):
            color = station_colors[station_code]
            ax5.scatter(dist, amp_diff_station, color=color, label=station_code,marker='o')


    
    legend_handles = [plt.Line2D([0], [0], marker='o', color='w', markersize=10, markerfacecolor=station_colors[station_code], label=station_code) for station_code in station_colors]
    fig1.legend(handles=legend_handles, title='Station Code', loc='outside right upper')
    ax3.set(xlabel='Depth [m]',ylabel='Amplitude diferences [m]')
    ax4.set(xlabel='Mw',ylabel='Amplitude diferences [m]')
    ax5.set(xlabel='Event-station distance [m]',ylabel='Amplitude diferences [m]')

    plt.show()
    input('Press enter')
    # Fit regression model
    # X = np.array(sta_event_dist_station).reshape(-1, 1)
    # y = np.array(amp_diff_all)
    # model = LinearRegression()
    # model.fit(X, y)
    # y_pred = model.predict(X)
    # plt.plot(sta_event_dist_station, y_pred, color='red', label='Linear Regression')

    
        

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