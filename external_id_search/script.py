from elasticsearch_dsl import Search, Q
from elasticsearch import Elasticsearch, helpers
from elasticsearch import RequestsHttpConnection
import argparse
import os
import glob
import json
import nltk
import logging
from dotenv import load_dotenv

import pandas as pd
import numpy as np
import logging
import re
import warnings
warnings.filterwarnings("ignore")



def db_connect():
    """Elasticsearch Connection on Sansa"""
    load_dotenv()
    
    DB_HOST = os.getenv("DB_HOST")
    USER_NAME = os.getenv("DB_USERNAME")
    PASSWORD = os.getenv("DB_PASSWORD")

    es = Elasticsearch([DB_HOST], connection_class=RequestsHttpConnection, http_auth=(USER_NAME, PASSWORD), verify_certs=False)
    return es


def query(target):
    es = db_connect()
    inputs = target.upper()
    query = {"query": {"match": {"text": f"{inputs}"}}} 
    test = es.search(index="meta", body=query, size=10000)["hits"]["hits"] 
    
    id_list = []
    if len(test) != 0 :
        for i in range(len(test)):
            map_id = test[i]['_source']['external_id']
            id_list.append(map_id)
    
    
    result = sorted(list(set(id_list)))
    return result
   

def main(args):
    keyword = args.target
    metadata_path = args.metadata
    meta_df = pd.read_csv(metadata_path)
    meta_df['tmp'] = meta_df['image_no'].str.split(".").str[0]

    results = query(keyword)
    # print(f' "{keyword}" exist in: {results}')

    tmp_df = meta_df[meta_df.tmp.isin(results)]

    print(f'"{keyword}" exist in:')
    for index, row in tmp_df.iterrows():
        print(f'{row.tmp} \t {row.title}')

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', type=str, default='east', help='')
    parser.add_argument('--metadata', type=str, default='/home/maplord/maplist_csv/luna_omo_metadata_56628_20220724.csv', help='')
    
    args = parser.parse_args()
    print(args)
    
    main(args)
    