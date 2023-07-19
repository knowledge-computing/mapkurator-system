import argparse
import logging

import pandas as pd

import elasticsearch
from elasticsearch import helpers

logging.basicConfig(level=logging.INFO)

def main(args):
    # elasticsearch connection 
    try:
        es = elasticsearch.Elasticsearch([{'host': '127.0.0.1', 'port': 9200}], timeout=1000)
        es_connected = es.ping()
    except:
        logging.warning('elasticsearch.ConnectionError.ElasticConnectionError while running %s', geojson_file.split("/")[-1])
        return
    if not es_connected:
        logging.warning('Error on elasticsearch connection while running %s', geojson_file.split("/")[-1])
        return
    es_logger = elasticsearch.logger
    es_logger.setLevel(elasticsearch.logging.WARNING)

    df = pd.read_csv(args.in_csv)

    for index, row in df.iterrows():
        if index % 1000 == 0: print(index, "processed ...")

        es_query = {"query": {
            "bool": {
            "must": [
                {
                "match": {'name': str(row['name']).lower().replace("'","\'")}
                }
            ]
            }
        }}

        try:
            osm_count = es.count(index="osm", body=es_query)["count"]
        except elasticsearch.ElasticsearchException as es_error:
            logging.warning('ElasticsearchException while running %s', geojson_file.split("/")[-1])
            continue
        
        # skip word that has more than 10000 matched cases in OSM
        if osm_count > 10000:
            # logging.info('ElasticsearchException while running %s', geojson_file.split("/")[-1])
            continue

        try:
            es_results = elasticsearch.helpers.scan(es, index="osm", query=es_query)
        except elasticsearch.ElasticsearchException as es_error:
            logging.warning('ElasticsearchException while running %s', geojson_file.split("/")[-1])
            continue

        es_results = [(hit["_source"]['source_table'], hit["_source"]['osm_id']) for hit in es_results]
        if len(es_results) == 0:
            # logging.info('No elasticsearch results of word %s while running %s', map_text, geojson_file.split("/")[-1])
            continue

        df.loc[index, 'source_table_osm_id'] = str(es_results)

    df = df.dropna()
    df.to_csv(args.out_csv, index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_csv', type=str, default='out.csv', help='input csv')
    parser.add_argument('--out_csv', type=str, default='./m6_entity_linker/osm_linker.csv', help='output csv')
    args = parser.parse_args()

    main(args)