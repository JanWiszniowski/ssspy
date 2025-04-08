"""
Function to calculate dutarion of first peak from quakeml file with mechanism data. As a result three arrays are created with event id, amplitude id and time.
"""

from obspy import read_events


def extract_delta_t(quakeml_file):
    events = read_events(quakeml_file, format='QUAKEML')
    result = {}
    amplitudes = {}
    
    # Iterate over events and extract time window information
    for event in events:
        if event.focal_mechanisms and len(event.focal_mechanisms) > 0:
            delta_t = {}
            m_amplitude = {}
            for amplitude in event.amplitudes:
                if amplitude.time_window:
                    channel_code = amplitude.waveform_id.channel_code
                    if channel_code.endswith('L') or channel_code.endswith('Z'):
                        m_amplitude[amplitude.waveform_id.station_code] = abs(amplitude.generic_amplitude)
                        delta_t[amplitude.waveform_id.station_code] = (amplitude.time_window.end - amplitude.time_window.begin)
                    
            result[event.resource_id.id] = delta_t
            amplitudes[event.resource_id.id] = m_amplitude
            print('Event peak duration:', event.resource_id.id)
        else:
            print('Event without mechanism')
            
    return result, amplitudes


def main(quakeml_file):
    delta_t, amplitudes = extract_delta_t(quakeml_file)
    return(delta_t, amplitudes)


#quakeml_file = 'dane\LGCD_zbiorcze.xml'
quakeml_file = 'dane\STH\STH2_corrected2.xml'
if __name__ == '__main__':
    main(quakeml_file)

