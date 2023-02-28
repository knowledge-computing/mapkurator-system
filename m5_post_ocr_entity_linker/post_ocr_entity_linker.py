import os
import argparse
import ast
import re
import pandas as pd
import numpy as np
import geojson

from dotenv import load_dotenv
from shapely.geometry import Polygon
import psycopg2

import elasticsearch
import elasticsearch.helpers

from post_ocr import lexical_search_query

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USERNAME, password=DB_PASSWORD)
cur = conn.cursor()
es = elasticsearch.Elasticsearch([{'host': "127.0.0.1", 'port': 9200}], timeout=1000)

def main(args):
    geojson_file = args.in_geojson_file
    output_dir = args.out_geojson_dir

    with open(geojson_file) as f:
        data = geojson.load(f)
        
        # find min, max geocoordinates from spotter results
        min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf') ,float('-inf')
        unique_map_text = []
        for feature_data in data['features']:
            map_pts = np.array(feature_data['geometry']['coordinates']).reshape(-1, 2)
            if min_x > min(map_pts[:, 0]): min_x = min(map_pts[:, 0])
            if min_y > min(map_pts[:, 1]): min_y = min(map_pts[:, 1])
            if max_x < max(map_pts[:, 0]): max_x = max(map_pts[:, 0])
            if max_y < max(map_pts[:, 1]): max_y = max(map_pts[:, 1])
            unique_map_text.append(str(feature_data['properties']['text']).lower())
        map_polygon = Polygon(np.array([[min_x, min_y], [min_x, max_y], [max_x, max_y], [max_x, min_y], [min_x, min_y]]))

        result_dict = dict()
        for map_text in set(unique_map_text):
            # ------------------------- post-ocr
            map_text_candidate = lexical_search_query(map_text)

            # ------------------------- entity linker
            if len(map_text_candidate) <= 3:
                result_dict[map_text] = (map_text_candidate, [])
                continue
            
            es_query = {'query': {'match': {'name': map_text_candidate.replace("'","\'")}}}
            try:
                es_results = elasticsearch.helpers.scan(es, index="osm", preserve_order=True, query=es_query)
            except elasticsearch.ElasticsearchException as es_error:
                print(es_error)
                result_dict[map_text] = (map_text_candidate, [])
                continue

            es_results = [(hit["_source"]['source_table'], hit["_source"]['osm_id']) for hit in es_results if hit["_source"]['osm_id'] is not None]
            
            output_osm_ids = []
            source_tables = set([table for table, _ in es_results])
            for source_table in source_tables:
                osm_ids = [osm_id for table, osm_id in es_results if table == source_table]
                if "points" in source_table:
                    sql = f"""SELECT osm_id
                            FROM  {source_table}
                            WHERE ST_CONTAINS(ST_TRANSFORM(ST_SetSRID(ST_MakeValid('{map_polygon}'), 3857), 4326), wkb_geometry)
                            AND osm_id = ANY (%s)
                    """
                    cur.execute(sql,(osm_ids,))
                    sql_result = cur.fetchall()

                    if len(sql_result) != 0:
                        output_osm_ids.extend([x[0] for x in sql_result])
                
                elif "line" in source_table or "polygon" in source_table:
                    sql = f"""SELECT osm_id
                            FROM  {source_table}
                            WHERE ST_INTERSECTS(ST_TRANSFORM(ST_SetSRID(ST_MakeValid('{map_polygon}'), 3857), 4326), wkb_geometry)
                            AND osm_id = ANY (%s)
                    """
                    cur.execute(sql,(osm_ids,))
                    sql_result = cur.fetchall()
                    if len(sql_result) != 0:
                        output_osm_ids.extend([x[0] for x in sql_result])

            result_dict[map_text] = (map_text_candidate, output_osm_ids)

        for feature_data in data['features']:
            feature_data["properties"]["postocr_label"] = result_dict[str(feature_data['properties']['text']).lower()][0]
            feature_data["properties"]["osm_id"] = result_dict[str(feature_data['properties']['text']).lower()][1]
   
    with open(os.path.join(output_dir, geojson_file.split("/")[-1]), 'w') as output_geojson:
        geojson.dump(data, output_geojson)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_geojson_file', type=str, default='data/100_maps_geojson_abc_geocoord/',
                        help='input dir for results of M4 geocoordinate converter')
    parser.add_argument('--out_geojson_dir', type=str, default='data/100_maps_geojson_abc_linked/',
                        help='output dir for converted geojson files')

    args = parser.parse_args()

    main(args)
