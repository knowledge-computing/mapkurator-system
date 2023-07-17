import os
import argparse
import ast
import re
import pandas as pd
import numpy as np
import geojson
import json
from dotenv import load_dotenv
from shapely.geometry import Polygon
import psycopg2
import reverse_geocoder as rg
import pycountry_convert as pc
from pyproj import Transformer, transform, Proj
import sys
import elasticsearch
import elasticsearch.helpers
from post_ocr import lexical_search_query
import logging
import time

logging.basicConfig(level=logging.INFO)



def save_postocr_results(in_geojson_data, unique_map_text_li, es_conn, output_dir, in_geojson_filename):
    result_dict_postocr = dict()
    for map_text in set(unique_map_text_li):
        map_text_candidate = lexical_search_query(map_text, es_conn)
        result_dict_postocr[map_text] = map_text_candidate

    for feature_data in in_geojson_data["features"]:
        feature_data["properties"]["postocr_label"] = result_dict_postocr[str(feature_data["properties"]["text"]).lower()]
    
    with open(os.path.join(output_dir, in_geojson_filename.split("/")[-1]), 'w', encoding='utf8') as output_geojson:
        geojson.dump(in_geojson_data, output_geojson, ensure_ascii=False)



def main(args):
    geojson_file = args.in_geojson_file
    output_dir = args.out_geojson_dir


    try:
        es = elasticsearch.Elasticsearch([{'host': "127.0.0.1", 'port': 9200}], timeout=1000)
        es_connected = es.ping()
    except:
        logging.warning('elasticsearch.ConnectionError.ElasticConnectionError while running %s', geojson_file.split("/")[-1])
        return
    if not es_connected:
        logging.warning('Error on elasticsearch connection while running %s', geojson_file.split("/")[-1])
        return
    es_logger = elasticsearch.logger
    es_logger.setLevel(elasticsearch.logging.WARNING)

    with open(geojson_file) as f:
        # Need update
        try: 
            data = geojson.load(f)
        except json.decoder.JSONDecodeError:
            if os.path.getsize(geojson_file) == 0:
                with open(os.path.join(output_dir, geojson_file.split("/")[-1]), 'w') as fp:
                    pass
            else:
                logging.info('JSONDecodeError %s', geojson_file)
            # sys.exit(1)
            return
        
        min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf') ,float('-inf')
        unique_map_text = []
        for feature_data in data['features']:
            unique_map_text.append(str(feature_data['properties']['text']).lower())
        
        if postocr_only:
            save_postocr_results(data, unique_map_text, es, output_dir, geojson_file)
            logging.info('Done generating standalone post-ocr geojson for %s', geojson_file.split("/")[-1])
            return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_geojson_file', type=str, default='data/100_maps_geojson_abc_geocoord/',
                        help='input geojson')
    parser.add_argument('--out_geojson_dir', type=str, default='data/100_maps_geojson_abc_linked/',
                        help='output dir for converted geojson files')

    args = parser.parse_args()

    main(args)