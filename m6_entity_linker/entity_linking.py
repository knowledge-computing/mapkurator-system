import os
import argparse
import ast
import logging
import time

import pandas as pd
import numpy as np
import geojson
import json

from shapely.ops import transform
from shapely.geometry import Polygon
import pyproj

import elasticsearch

from dotenv import load_dotenv
import psycopg2
from postgres_logger import LinkerLoggingConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(args):
    input_dir = args.in_geojson_dir
    output_dir = args.out_geojson_dir

    # elasticsearch connection 
    try:
        es = elasticsearch.Elasticsearch([{'host': '127.0.0.1', 'port': 9200}], timeout=1000)
        es_connected = es.ping()
    except:
        logging.warning('elasticsearch.ConnectionError.ElasticConnectionError')
        return
    if not es_connected:
        logging.warning('Error on elasticsearch connection')
        return
    es_logger = elasticsearch.logger
    es_logger.setLevel(elasticsearch.logging.WARNING)

    # postgres connection 
    load_dotenv()
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USERNAME, password=DB_PASSWORD, port=DB_PORT, connection_factory=LinkerLoggingConnection)
    except Exception as e:
        logging.warning('Error on psycopg2 connection ', e)
        return

    sample_map_df = pd.read_csv(args.sample_map_path, dtype={'image_no': str})
    sample_map_df['image_no'] = sample_map_df['image_no'].str.replace('.1.jp2', '', regex=False).str.replace('.jp2', '', regex=False)
    sample_map_df['image_no'] = sample_map_df['image_no'].apply(lambda x: x[:-2] if x[-2:] == '.1' else x)

    conn.initialize(logger)
    conn.autocommit = True

    with conn.cursor() as cur:
        for index, record in sample_map_df.iterrows():
            input_geojson_file = os.path.join(input_dir, record.image_no + ".geojson")
        
            if not os.path.exists(input_geojson_file):
                logging.warning('PostOCR output does not exist %s', record.image_no + ".geojson")
                continue
            
            if os.path.exists(os.path.join(output_dir, input_geojson_file.split("/")[-1])):
                logging.info('EntityLinker output already exists %s', record.image_no + ".geojson")
                continue

            with open(input_geojson_file) as f:
                try: 
                    data = geojson.load(f)
                except json.decoder.JSONDecodeError:
                    if os.path.getsize(input_geojson_file) == 0:
                        with open(os.path.join(output_dir, input_geojson_file.split("/")[-1]), 'w') as fp:
                            continue
                    else:
                        logging.info('JSONDecodeError %s', input_geojson_file)
                        continue

                for feature_data in data['features']:
                    map_text = str(feature_data['properties']['postocr_label'])

                    # skip null geometry
                    if feature_data['geometry'] is None:
                        feature_data["properties"]["osm_id"] = []
                        continue
                    
                    # skip text less than 3 characters
                    if len(map_text) <= 3:
                        feature_data["properties"]["osm_id"] = []
                        continue

                    pts = np.array(feature_data['geometry']['coordinates']).reshape(-1, 2)
                    map_polygon = Polygon(pts)

                    es_query = {
                        "bool": {
                        "must": [
                            {
                            "match": {'name': map_text.lower().replace("'","\'")}
                            }
                        ]
                        }
                    }

                    try:
                        es_results = es.search(index="osm-linker", query=es_query)
                    except elasticsearch.ElasticsearchException as es_error:
                        logging.warning('ElasticsearchException while running %s', input_geojson_file.split("/")[-1])
                        continue

                    if es_results['hits']['total']['value'] == 0:
                        # logging.info('No elasticsearch results of word %s while running %s', map_text, input_geojson_file.split("/")[-1])
                        feature_data["properties"]["osm_id"] = []
                        continue

                    es_results = [ast.literal_eval(hit["_source"]['source_table_osm_id']) for hit in es_results['hits']['hits']][0]
                    output_osm_ids = []
                    source_tables = set([table for table, _ in es_results if "other_relations" not in table])

                    for source_table in source_tables:
                        sql = ""
                        osm_ids = [osm_id for table, osm_id in es_results if table == source_table]

                        if "points" in source_table:
                            sql = f"""SELECT osm_id
                                    FROM  {source_table}
                                    WHERE ST_CONTAINS(ST_TRANSFORM(ST_SetSRID(ST_MakeValid('{map_polygon}'), 3857), 4326), wkb_geometry)
                                    AND osm_id = ANY (%s)
                            """
                        
                        elif "line" in source_table:
                            sql = f"""SELECT osm_id
                                    FROM  {source_table}
                                    WHERE ST_INTERSECTS(ST_TRANSFORM(ST_SetSRID(ST_MakeValid('{map_polygon}'), 3857), 4326), wkb_geometry)
                                    AND osm_id = ANY (%s)
                            """

                        elif "polygon" in source_table:
                            sql = f"""SELECT osm_id
                                    FROM  {source_table}
                                    WHERE ST_INTERSECTS(ST_TRANSFORM(ST_SetSRID(ST_MakeValid('{map_polygon}'), 3857), 4326), ST_MakeValid(wkb_geometry, 'method=structure'))
                                    AND osm_id = ANY (%s)
                            """

                        try:
                            cur.execute(sql,(osm_ids,))
                        except Exception as e:
                            logging.warning('Error occured while executing sql for %s', input_geojson_file.split("/")[-1], e)
                            if "TopologyException" in repr(e):
                                continue
                            else:
                                return
                            
                        sql_result = cur.fetchall()
                        if len(sql_result) != 0:
                            output_osm_ids.extend([x[0] for x in sql_result])

                    feature_data["properties"]["osm_id"] = output_osm_ids

            with open(os.path.join(output_dir, input_geojson_file.split("/")[-1]), 'w', encoding='utf8') as output_geojson:
                geojson.dump(data, output_geojson, ensure_ascii=False)
            logging.info('Done generating geojson for %s', input_geojson_file.split("/")[-1])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample_map_path', type=str, default='data/initial_US_100_maps.csv',
                        help='path to sample map csv, which contains gcps info')
    parser.add_argument('--in_geojson_dir', type=str, default='data/100_maps_geojson_abc_geocoord/',
                        help='input geojson')
    parser.add_argument('--out_geojson_dir', type=str, default='data/100_maps_geojson_abc_linked/',
                        help='output dir for converted geojson files')
    args = parser.parse_args()
    main(args)
