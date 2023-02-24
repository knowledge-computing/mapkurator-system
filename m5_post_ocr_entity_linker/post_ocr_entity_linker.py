import os
import argparse
import ast
from dotenv import load_dotenv
import re
import pandas as pd
import numpy as np
import geojson
import sqlalchemy
from sqlalchemy import create_engine
from shapely.geometry import Polygon
from post_ocr import lexical_search_query

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

connection_string = f'postgresql://postgres:{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}'


def main(args):
    geojson_file = args.in_geojson_file
    output_dir = args.out_geojson_dir

    sample_map_df = pd.read_csv(args.sample_map_path, dtype={'external_id': str})
    sample_map_df['external_id'] = sample_map_df['external_id'].str.strip("'").str.replace('.', '', regex=True)
    row = sample_map_df[sample_map_df['external_id'] == geojson_file.split("/")[-1].split(".")[0]]
    # gcps = ast.literal_eval(row.iloc[0]['gcps'])

    with open(geojson_file) as f:
        data = geojson.load(f)
        for feature_data in data['features']:
            map_pts = np.array(feature_data['geometry']['coordinates']).reshape(-1, 2)
            map_text = str(feature_data['properties']['text'])

            # ------------------------- post-ocr
            map_text_candidate = lexical_search_query(map_text)
            feature_data["properties"]["postocr_label"] = map_text_candidate
            
            # ------------------------- entity linker
            # 1. retrieve all osm ids using elasticsearch osm id
            # hint 1. query substring match (sample query is shown as below)
            # '''
            # {"query": {
            #     "query_string" : {"default_field" : "name", "query" : "*Lake*"}
            # } }
            # '''
            # hint 2. search_type and size are required to retrieve all possible entries in osm index
            # resp = requests.get(f'http://localhost:9200/osm/_search?search_type=query_then_fetch&scroll=10m&size=100', \
            # data=query.encode("utf-8"), \
            # headers = headers)


            # 2. with all osm ids, use postgres to query spatial relation (if the osm feature is in map boundary)

            

    # ------------------------- entity linker
    # with open(os.path.join(output_dir, geojson_file.split("/")[-1]), 'w') as output_geojson:
    #     geojson.dump(data, output_geojson)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample_map_path', type=str, default='data/initial_US_100_maps.csv',
                        help='path to sample map csv, which contains map boundary info')
    parser.add_argument('--in_geojson_file', type=str, default='data/100_maps_geojson_abc_geocoord/',
                        help='input dir for results of M4 geocoordinate converter')
    parser.add_argument('--out_geojson_dir', type=str, default='data/100_maps_geojson_abc_linked/',
                        help='output dir for converted geojson files')

    args = parser.parse_args()

    main(args)
