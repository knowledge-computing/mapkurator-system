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
import reverse_geocoder as rg
import pycountry_convert as pc
from pyproj import Transformer, transform, Proj

import elasticsearch
import elasticsearch.helpers
from post_ocr import lexical_search_query
import logging
import time

logging.basicConfig(level=logging.INFO)

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")



def main(args):
    geojson_file = args.in_geojson_file
    output_dir = args.out_geojson_dir
    postocr_only = args.module_post_ocr_only

    try:
        es = elasticsearch.Elasticsearch([{'host': "127.0.0.1", 'port': 9200}], timeout=1000)
        es_connected = es.ping()
    except:
        logging.warning('elasticsearch.ConnectionError.ElasticConnectionError while running %s.' % geojson_file)
        return
    if not es_connected:
        logging.warning('Error on elasticsearch connection while running %s.' % geojson_file)
        return

    with open(geojson_file) as f:
        data = geojson.load(f)

        min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf') ,float('-inf')
        unique_map_text = []
        for feature_data in data['features']:
            map_pts = np.array(feature_data['geometry']['coordinates']).reshape(-1, 2)
            if min_x > min(map_pts[:, 0]): min_x = min(map_pts[:, 0])
            if min_y > min(map_pts[:, 1]): min_y = min(map_pts[:, 1])
            if max_x < max(map_pts[:, 0]): max_x = max(map_pts[:, 0])
            if max_y < max(map_pts[:, 1]): max_y = max(map_pts[:, 1])
            unique_map_text.append(str(feature_data['properties']['text']).lower())

        if postocr_only:
            result_dict_postocr = dict()
            for map_text in set(unique_map_text):
                map_text_candidate = lexical_search_query(map_text, es)
                result_dict_postocr[map_text] = map_text_candidate

            for feature_data in data["features"]:
                feature_data["properties"]["postocr_label"] = result_dict_postocr[str(feature_data["properties"]["text"]).lower()]

            with open(os.path.join(output_dir, geojson_file.split("/")[-1]), 'w', encoding='utf8') as output_geojson:
                geojson.dump(data, output_geojson, ensure_ascii=False)

            logging.info('Done generating geojson for %s', geojson_file.split("/")[-1])
            return

        try:
            conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USERNAME, password=DB_PASSWORD)
        except:
            logging.warning('Error on psycopg2 connection while running %s.' % geojson_file)
            return

        cur = conn.cursor()
        continent_to_tablename_dict = {
            "NA": "north_america",
            "SA": "south_america",
            "AS": "asia",
            "AF": "africa",
            "OC": "australia_oceania",
            "EU": "europe",
            "AN" : "antarctica"
        }

        table_names = ['points', 'lines', 'multilinestrings', 'multipolygons', 'other_relations']

        map_pts = np.array([[min_x, min_y], [min_x, max_y], [max_x, max_y], [max_x, min_y], [min_x, min_y]])
        map_polygon = Polygon(map_pts)

        transformer = Transformer.from_crs("epsg:3857", "epsg:4326")
        transformed_map_pts = np.empty(map_pts.shape)
        transformed_map_pts[:, 1], transformed_map_pts[:, 0] = transformer.transform(map_pts[:, 1], map_pts[:, 0])
        geocode_results = rg.search(tuple(map(tuple, transformed_map_pts)), mode=1)
        continents = []
        for geocode_result in geocode_results:
            li = continent_to_tablename_dict[pc.country_alpha2_to_continent_code(geocode_result['cc'])]
            continents.extend([li])
        continents = list(set(continents))
        if "north_america" in continents:
            continents.append("central_america")

        if len(continents) != 1:
            logging.warning('More than one continent to query - %s.' % geojson_file)
            return

        continents = [continent + "." + table_name for continent in continents for table_name in table_names]
        result_dict = dict()

        for map_text in set(unique_map_text):
            map_text_candidate = lexical_search_query(map_text, es)

            if len(map_text_candidate) <= 3:
                result_dict[map_text] = (map_text_candidate, [])
                continue

            es_query = {"query": {
                "bool": {
                "must": [
                    {
                    "terms": {"source_table": continents}
                    },
                    {
                    "match": {'name': map_text_candidate.replace("'","\'")}
                    }
                ]
                }
            }}

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
                    # print(sql)
                    # print(osm_ids)
                    # print("point contains starts: # of features", len(osm_ids))
                    # start = time.time()
                    cur.execute(sql,(osm_ids,))
                    sql_result = cur.fetchall()
                    # print("time:", time.time() - start)
                    if len(sql_result) != 0:
                        output_osm_ids.extend([x[0] for x in sql_result])

                elif "line" in source_table or "polygon" in source_table:
                    sql = f"""SELECT osm_id
                            FROM  {source_table}
                            WHERE ST_INTERSECTS(ST_TRANSFORM(ST_SetSRID(ST_MakeValid('{map_polygon}'), 3857), 4326), wkb_geometry)
                            AND osm_id = ANY (%s)
                    """
                    # print(sql)
                    # print(osm_ids)
                    # print("polygon, line intersect starts: # of features", len(osm_ids))
                    # start = time.time()
                    cur.execute(sql,(osm_ids,))
                    sql_result = cur.fetchall()
                    # print("time:", time.time() - start)
                    if len(sql_result) != 0:
                        output_osm_ids.extend([x[0] for x in sql_result])

            result_dict[map_text] = (map_text_candidate, output_osm_ids)

        for feature_data in data['features']:
            feature_data["properties"]["postocr_label"] = result_dict[str(feature_data['properties']['text']).lower()][0]
            feature_data["properties"]["osm_id"] = result_dict[str(feature_data['properties']['text']).lower()][1]

    with open(os.path.join(output_dir, geojson_file.split("/")[-1]), 'w', encoding='utf8') as output_geojson:
        geojson.dump(data, output_geojson, ensure_ascii=False)
    logging.info('Done generating geojson for %s', geojson_file.split("/")[-1])



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_geojson_file', type=str, default='data/100_maps_geojson_abc_geocoord/',
                        help='input geojson')
    parser.add_argument('--out_geojson_dir', type=str, default='data/100_maps_geojson_abc_linked/',
                        help='output dir for converted geojson files')
    parser.add_argument('--module_post_ocr_only', default=False, action='store_true',
                        help='postOCR only')

    args = parser.parse_args()

    main(args)