import os
import argparse 
import geojson
import geocoder
import json
import time
import pdb


def arcgic_geocoding(place_name, maxRows = 5):
    try:
        response = geocoder.arcgis(place_name,maxRows=maxRows)
        return response.json
    except exception as e:
        print(e)
        return -1
    
    
def google_geocoding(place_name, api_key = None, maxRows = 5):
    try:
        response = geocoder.google(place_name, key=api_key, maxRows = maxRows)
        return response.json
    except exception as e:
        print(e)
        return -1
        
def osm_geocoding(place_name,  maxRows = 5):
    try:
        response = geocoder.osm(place_name,  maxRows = maxRows)
        return response.json
    except exception as e:
        print(e)
        return -1   
    

def geonames_geocoding(place_name, user_name = None, maxRows = 5):
    try:
        response = geocoder.geonames(place_name, key = user_name,  maxRows=maxRows)
        # hourly limit of 1000 credits
        time.sleep(4)
        return response.json
    except exception as e:
        print(e)
        return -1
        

def geocoding(args):
    output_folder = args.output_folder
    input_map_geojson_path =  args.input_map_geojson_path
    api_key = args.api_key
    user_name = args.user_name
    geocoder_option = args.geocoder_option
    max_results = args.max_results
    suffix = args.suffix

    with open(input_map_geojson_path, 'r') as f:
        data = geojson.load(f)

    map_name = os.path.basename(input_map_geojson_path).split('.')[0]
    output_folder = os.path.join(output_folder, geocoder_option)

    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)

    output_path = os.path.join(output_folder, map_name) + '.json'

    with open(output_path, 'w') as f:
        pass # flush output file
    
    features = data['features']
    for feature in features: # iterate through all the detected text labels
        geometry = feature['geometry']
        text = feature['properties']['text']
        score = feature['properties']['score']

        # suffix = ', Los Angeles'
        text = str(text) + suffix

        print(text)

        if geocoder_option == 'arcgis':
            results = arcgic_geocoding(text, maxRows = max_results)
        elif geocoder_option == 'google':
            results = google_geocoding(text, api_key = api_key, maxRows = max_results)
        elif geocoder_option == 'geonames':
            results = geonames_geocoding(text, user_name = user_name, maxRows = max_results)
        elif geocoder_option == 'osm':
            results = osm_geocoding(text, maxRows = max_results)
        else:
            raise NotImplementedError

        if results == -1:
            # geocoder can not find match
            pass 
        else:
            # save results 
            with open(output_path, 'a') as f:
                json.dump({'text':text, 'score':score, 'geometry': geometry, 'geocoding':results}, f)
                f.write('\n')

        # pdb.set_trace()


def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--output_folder', type=str, default='/data2/sanborn_maps_output/LA_sanborn/geocoding/')
    parser.add_argument('--input_map_geojson_path', type=str, default='/data2/sanborn_maps_output/LA_sanborn/geojson_testr/service-gmd-gmd436m-g4364m-g4364lm-g4364lm_g00656189401-00656_01_1894-0001l.geojson')
    parser.add_argument('--api_key', type=str, default=None, help='Specify API key if needed')
    parser.add_argument('--user_name', type=str, default=None, help='Specify user name if needed')

    parser.add_argument('--suffix', type=str, default=None, help='placename suffix (e.g. city name)')
    
    parser.add_argument('--max_results', type=int, default=5, help='max number of results returend by geocoder')

    parser.add_argument('--geocoder_option', type=str, default='arcgis', 
        choices=['arcgis', 'google','geonames','osm'], 
        help='Select text spotting model option from ["arcgis","google","geonames","osm"]') # select text spotting model

                        
    args = parser.parse_args()
    print('\n')
    print(args)
    print('\n')

    if not os.path.isdir(args.output_folder):
        os.makedirs(args.output_folder)

    geocoding(args)


if __name__ == '__main__':

    main()

    

