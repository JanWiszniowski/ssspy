"""
Simple seismic simulation
-------------------------

:copyright:
    Jan Wiszniowski (jwisz@igf.edu.pl)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
:version 0.0.1:
    2025-02-07

The program print displacements in near, far in time domain for various distances
and in separate subplots for various source parameters: scalar moment and rupture time.

:call: *python ssspy.py config.json*, where *config.json* is a configuration file
    (see :ref:`configuration`)

"""
import numpy as np
import matplotlib.pyplot as plt
from source_models import get_time_source_model
from green_functions import get_green_function

DEFAULT_MOMENT_SCALARS = [10 ** ((mw * 1.5) + 9.1) for mw in [1, 2, 4]]
DEFAULT_SOURCE_TIMES = [0.1, 0.3, 0.5]
DEFAULT_SOURCE_PARAMETERS = [{'moment_scalar': DEFAULT_MOMENT_SCALARS[idx], 'rupture_time': DEFAULT_SOURCE_TIMES[idx]}
                             for idx in range(min(len(DEFAULT_MOMENT_SCALARS), len(DEFAULT_SOURCE_TIMES)))]
DEFAULT_DISTANCES = [200, 500, 1000, 5000, 20000]


def time_simulate(configuration, distance, source_parameters, ax=None):
    """
    The time_simulate function simulate and optionally plots the displacement simulation
    in near, intermediate and fal fields for given distance, and source parameters

    :param configuration: The configuration container of all parameters dictionary required for the program to work.
    :type configuration: dict
    :param distance: The hypocentral distance in meters
    :type distance: float
    :param source_parameters:
    :type source_parameters: dict
    :param ax: An object encapsulating an individual subplot in a figure.
        Missing or None parameter turn off plotting.
    :type ax: Matplotlib.Axes
    :return: The tuple of values:

        * The time :math:`t_{max}` from the rupture beginning, where displacement reaches the maximum value,
        * The maximum displacement,
        * The displacement in the near field at :math:`t_{max}`,
        * The displacement in the intermediate field at :math:`t_{max}`,
        * The displacement in the far field at :math:`t_{max}`,
        * The maximum displacement in the far field.

    :rtype: tuple(float, float, float, float, float, float)

    """
    source_model = get_time_source_model(configuration, source_parameters)
    dt = configuration.get('dt', 0.001)
    green_function = get_green_function(configuration, dt, configuration.get('density', 2700),
                                        radial_radiation=configuration.get('radial_radiation', 0.52))
    vp = configuration.get('vp', 5000.0)
    vs = configuration.get('vs', vp / np.sqrt(3))
    # if tp is None:
    #     tp = distance / vp
    # if ts is None:
    #     ts = distance / vs
    rupture_time = source_parameters['rupture_time']
    stop_simulation = configuration.get('stop_simulation', 'phase_time')
    oxtail_view = configuration.get('oxtail_view', 'rupture_time')
    times = np.arange(0.0, distance / vs + rupture_time + 1.0, dt)
    near_field, _ = green_function.near(source_model, distance, vp, vs, times)
    intermediate_field, _ = green_function.intermediate(source_model, distance, vp, vs, times)
    far_field, _ = green_function.far(source_model, distance, vp, vs, times)
    p_s = distance / vs - distance / vp
    if isinstance(stop_simulation, float) or isinstance(stop_simulation, int):
        final_index = np.min(np.array([far_field.size, intermediate_field.size, near_field.size,
                                       int(np.ceil(stop_simulation / dt))]))
    elif stop_simulation == 'phase_time':
        final_index = np.min(np.array([far_field.size, intermediate_field.size, near_field.size, np.ceil(p_s / dt)]))
    elif stop_simulation == 'phase_time...':
        final_index = np.min(np.array([far_field.size, intermediate_field.size, near_field.size, np.ceil(p_s / dt)]))
    elif stop_simulation == 'rupture_time':
        final_index = np.min(np.array([far_field.size, intermediate_field.size, near_field.size,
                                       np.ceil((p_s + rupture_time + 0.2) / dt)]))
    else:
        final_index = np.min(np.array([far_field.size, intermediate_field.size, near_field.size]))
    final_index = int(final_index)
    far_field[0] = 0.0
    near_field[0:final_index] += 1.0e-12
    intermediate_field[0:final_index] += 1.0e-12
    far_field[0:final_index] + - 1.0e-12
    plt_near_field = near_field[0:final_index]
    plt_intermediate_field = intermediate_field[0:final_index]
    plt_far_field = far_field[0:final_index]
    plt_times = times[0:final_index] + distance / vp
    plt_all_fields = plt_near_field + plt_intermediate_field + plt_far_field
    maximum_pointer = configuration.get('maximum_pointer', 'end')
    if maximum_pointer == 'min_tau_tp':
        max_end = int(np.min([rupture_time / dt, p_s / dt, final_index]))
    else:
        max_end = final_index
    idx = np.argmax(plt_all_fields[0:max_end])
    # max_far = np.max(plt_far_field)
    if ax is not None:
        ax.plot(plt_times, plt_near_field, 'r')
        ax.plot(plt_times, plt_intermediate_field, 'g')
        ax.plot(plt_times, plt_far_field + 1.0e-12, 'b')
        ax.plot(plt_times, plt_all_fields, 'k')
        ax.plot([plt_times[idx]], [plt_all_fields[idx]], 'k*')
        ax.plot([plt_times[idx], plt_times[idx]], [plt_all_fields[idx], 1.0e-12], 'k:')
        ax.text(plt_times[idx], plt_all_fields[idx]*1.2, f'{distance/1000.0:.1f} km')
        ax.set_xlim([0, plt_times[-1]])
        if stop_simulation == 'phase_time...':

            if isinstance(oxtail_view, float) or isinstance(oxtail_view, int):
                oxtail_index = np.min(np.array([far_field.size, intermediate_field.size, near_field.size,
                                                int(np.ceil(oxtail_view / dt))]))
            elif oxtail_view == 'rupture_time':
                oxtail_index = np.min(np.array([far_field.size, intermediate_field.size, near_field.size,
                                               int(np.ceil((p_s + rupture_time + 0.2) / dt))]))
            else:
                oxtail_index = int(np.min(np.array([far_field.size, intermediate_field.size, near_field.size])))
            if oxtail_index > final_index:
                oxtail_times = times[final_index:oxtail_index] + distance / vp
                oxtail_near_field = near_field[final_index:oxtail_index]
                oxtail_intermediate_field = intermediate_field[final_index:oxtail_index]
                oxtail_far_field = far_field[final_index:oxtail_index]
                oxtail_all_fields = oxtail_near_field + oxtail_intermediate_field + oxtail_far_field
                ax.plot(oxtail_times, oxtail_near_field, 'r:')
                ax.plot(oxtail_times, oxtail_intermediate_field, 'g:')
                ax.plot(oxtail_times, oxtail_far_field + 1.0e-12, 'b:')
                ax.plot(oxtail_times, oxtail_all_fields, 'k:')
                ax.set_xlim([0, oxtail_times[-1]])
        ax.set_yscale(configuration.get('yscale', 'log'))
    # return times[idx], plt_all_fields[idx], plt_near_field[idx], plt_intermediate_field[idx],\
    #     plt_far_field[idx], max_far
    return times[idx], plt_all_fields[idx], plt_near_field[idx], plt_intermediate_field[idx], plt_far_field[idx]


def plot_simulations_radial_p(configuration):
    """
    Plots the figure containing P wave displacement in radial direction simulation
    for various source parameters in separate subplots.
    The configuration parameters must contain all required information for simulation and plotting.
    This procedure runs, when you call ssspy program.

    :param configuration: The configuration container of all parameters dictionary required for the program to work.
    :type configuration: dict

    """
    source_parameters = configuration.get('source_parameters', DEFAULT_SOURCE_PARAMETERS)
    distances = configuration.get('distances', DEFAULT_DISTANCES)
    plot_size = configuration.get('plot_size', [4, 4])
    fig, axis = plt.subplots(nrows=len(source_parameters), ncols=1, sharex='col', figsize=tuple(plot_size))
    for m_idx, current_source_parameters in enumerate(source_parameters):
        ax = axis[m_idx]
        ymin = 1e6
        ymax = 0
        for distance in distances:
            # _, al, _, _, _, _ = time_simulate(configuration, distance, current_source_parameters, ax=ax)
            _, al, _, _, _ = time_simulate(configuration, distance, current_source_parameters, ax=ax)
            if ymin > al:
                ymin = al
            if ymax < al:
                ymax = al
        ax.set_ylim([ymin / 100, ymax * 5])
        moment_scalar = current_source_parameters['moment_scalar']
        ax.set(ylabel='Displacement [m]',
               title=r"{}) $M_0={:.1e},\ M_w={:.1f},\ \tau={:.2f}$".format(chr(97 + m_idx), moment_scalar,
                                                                        2 / 3 * np.log10(moment_scalar) - 6.07,
                                                                        current_source_parameters['rupture_time']))
    axis[-1].set(xlabel='Time from the rupture beginning [s]')
    source_model = configuration.get('source_model', '')
    green_function = configuration.get('green_function', 'homogeneous')
    fig.savefig(f'{source_model}_{green_function}.png')
    plt.show(block=True)


if __name__ == '__main__':
    import sys
    import json

    if len(sys.argv) < 2:
        print('call: python ssspy.py config.json')
        sys.exit()
    with open(sys.argv[1], "r") as f:
        Configuration = json.load(f)
        plot_simulations_radial_p(Configuration)
