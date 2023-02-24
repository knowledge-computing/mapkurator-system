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

    # check if first pair of gcps is in midwest-US
    regex = re.compile('[^a-zA-Z]')
    conn = create_engine(connection_string, echo=False)
    sample_map_df = pd.read_csv(args.sample_map_path, dtype={'external_id': str})
    sample_map_df['external_id'] = sample_map_df['external_id'].str.strip("'").str.replace('.', '')

    geojson_files = os.listdir(args.in_geojson_dir)
    for i, geojson_file in enumerate(geojson_files):
        row = sample_map_df[sample_map_df['external_id']==geojson_file.split(".")[0]]
        gcps = ast.literal_eval(row.iloc[0]['gcps'])
        with open(args.in_geojson_dir + geojson_file) as f:
            data = geojson.load(f)
            for feature_data in data['features']:
                map_pts = np.array(feature_data['geometry']['coordinates']).reshape(-1, 2)
                map_text = str(feature_data['properties']['text'])

                ########## post-ocr
                map_text_candidate = lexical_search_query(map_text)
                feature_data["properties"]["postocr_label"] = map_text_candidate

                ########## entity linker
                map_polygon = Polygon(map_pts)
                feature_data['properties']['osm_id'] = []

                    # query = f"""SELECT p.ogc_fid
                    #     FROM  polygon_features p
                    #     WHERE LOWER(p.name) LIKE '%%{map_text}%%'
                    #     AND ST_INTERSECTS(ST_TRANSFORM(ST_SetSRID(ST_MakeValid('{map_polygon}'::geometry), 4326)::geometry, 4326), p.wkb_geometry);
                    # """
        #
        #             try:
        #                 intersect_df = pd.read_sql(query, con=conn)
        #             except sqlalchemy.exc.InternalError:
        #                 continue
        #
        #             if not intersect_df.empty:
        #                 feature_data['properties']['osm_ogc_fid'] = intersect_df['ogc_fid'].values.tolist()
        #             # else:
        #             #     feature_data['properties']['osm_ogc_fid'] = []

            with open(args.out_geojson_dir+geojson_file, 'w') as output_geojson:
                geojson.dump(data, output_geojson)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample_map_path', type=str, default='data/initial_US_100_maps.csv',
                        help='path to sample map csv, which contains map boundary info')
    parser.add_argument('--in_geojson_dir', type=str, default='data/100_maps_geojson_abc_geocoord/',
                        help='input dir for results of M4 geocoordinate converter')
    parser.add_argument('--out_geojson_dir', type=str, default='data/100_maps_geojson_abc_linked/',
                        help='output dir for converted geojson files')

    args = parser.parse_args()

    main(args)
