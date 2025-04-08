"""
Function to calculate dutarion of first peak from quakeml file with mechanism data. As a result three arrays are created with event id, amplitude id and time.
"""

from obspy import read_events


def extract_moment(quakeml_file):
    events = read_events(quakeml_file, format ='QUAKEML')
    moment = {}
    # Iterate over events and extract time window information
    for event in events:
        if event.focal_mechanisms and len(event.focal_mechanisms) > 0:          
            for mechanism in event.focal_mechanisms:
                if mechanism.moment_tensor.inversion_type == 'general':
                    moment[event.resource_id.id] = mechanism.moment_tensor.scalar_moment
                    
            print('Scalar moment:',event.resource_id.id)
        else:
            print('Event without mechanism')
    return(moment)

def main(quakeml_file):
    m0 = extract_moment(quakeml_file)
    return(m0)


quakeml_file = 'dane\STH\STH2_corrected2.xml'
#quakeml_file = 'dane\LGCD_zbiorcze.xml'
if __name__ == '__main__':
    main(quakeml_file)

