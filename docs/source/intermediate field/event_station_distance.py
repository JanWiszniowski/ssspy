"""
Function to calculate event-reciever distance from the data stored in quakeml and dataless files.
"""



from obspy import read_events
from obspy import read_inventory
import numpy as np
import glob
import matplotlib.pyplot as plt

def extract_event_location(quakeml_file):
    # Read events from QuakeML file
    events = read_events(quakeml_file, format = "QUAKEML" )
    latitude = []
    longitude = []
    depth = []
    preferred_origin = []

    # Iterate over events and find the preferred origin
    for event in events:
        if event.focal_mechanisms:
            pref_origin = event.preferred_origin_id.id
            for origin in event.origins:
                if origin.resource_id.id == pref_origin:
                    # Extract location and depth information
                    latitude.append(origin.latitude)
                    longitude.append(origin.longitude)
                    depth.append(origin.depth * 1000.0)
                    preferred_origin.append(pref_origin)
        else:
            print('Event without mechanism')
    return latitude, longitude, depth, preferred_origin

    return None  # Return None if preferred_origin_id is not found

def calculate_distance(lat1, lon1, depth1, lat2, lon2, depth2):
    delta_lat = np.radians(lat2 - lat1)
    delta_lon = np.radians(lon2 - lon1)
    #haversine formula
    a = np.sin(delta_lat / 2) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(delta_lon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = 6371 * c * 1000  
    depth_difference = np.abs(depth2 - depth1)

    return np.sqrt(distance**2 + depth_difference**2)

def extract_station_locations(dataless_files):
    inventory = read_inventory(dataless_files)
    station_locations = {}
    for network in inventory:
        for station in network:
            station_locations[station.code] = {
                'latitude': station.latitude,
                'longitude': station.longitude,
                'elevation': station.elevation
            }

    return station_locations


def get_dataless_files(directory, network_code):
    pattern = f"{directory}/{network_code}*.dataless"
    return glob.glob(pattern)


class EventMech:
    def __init__(self,event_id, event_location):
        self.id = event_id
        self.location = event_location
        self.stations = []


class Station(EventMech):
    def __init__(self,code, distance):
        super().__init__(event_id=None, event_location=None)
        self.code = code
        self.sta_event_distance = distance

    


def main(quakeml_file, directory, network_code):
    # Extract event location
    event_latitude, event_longitude, event_depth, preferred_origin = extract_event_location(quakeml_file)
    cat = []
    all_distance=[]
    for idx in enumerate(preferred_origin):

        if event_latitude:
            event_location = event_latitude[idx[0]], event_longitude[idx[0]], event_depth[idx[0]]
            cat.append(EventMech(preferred_origin[idx[0]], event_location)) 
            #print(f"Event Location: Latitude={event_latitude}, Longitude={event_longitude}, Depth={event_depth} m")

            # Iterate over dataless files
            dataless_list = get_dataless_files(directory, network_code)
            for dataless_file in dataless_list:
                station_locations = extract_station_locations(dataless_file)

                # Calculate event-station distances
                for station_code, station_info in station_locations.items():
                    
                    station_latitude = station_info['latitude']
                    station_longitude = station_info['longitude']
                    station_elevation = station_info['elevation']

                    distance=calculate_distance(
                        event_latitude[idx[0]], event_longitude[idx[0]], event_depth[idx[0]],
                        station_latitude, station_longitude, station_elevation
                    )
                    cat[idx[0]].stations.append(Station(station_code, distance))
                    all_distance.append(distance/1000)
        print('Event station distance:',idx)

    return(cat, all_distance)

# Example usage
quakeml_file_path = 'EventParameterssmi_igf.edu.pl_LUMINEOS_eventParameters.xml'
directory = 'datalessLGCD'
network_code = 'PL'

catalog, distances = main(quakeml_file_path, directory, network_code)
plt.hist(distances)
plt.xlabel('Event-station distance [km]')
plt.ylabel('Number of events')
plt.title('LGCD event-station distances distribution')
plt.show()