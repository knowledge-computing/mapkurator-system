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
import datetime
import pandas as pd
import numpy as np
import logging
import re
import warnings
warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO)

def db_connect():
    """Elasticsearch Connection on Sansa"""
    
    load_dotenv()
    
    DB_HOST = os.getenv("DB_HOST")
    USER_NAME = os.getenv("DB_USERNAME")
    PASSWORD = os.getenv("DB_PASSWORD")

    es = Elasticsearch([DB_HOST], connection_class=RequestsHttpConnection, http_auth=(USER_NAME, PASSWORD), verify_certs=False)
    
    return es



def query(args):
    """ Query candidates and save them as 'postocr_label' """
    
    es = db_connect()

    input_dir = args.in_geojson_dir
    output_geojson = args.out_geojson_dir

    map_name_output = input_dir.split('/')[-1]

    with open(input_dir) as json_file:
        json_df = json.load(json_file)
        if json_df != {}:  
            query_result = []
            for i in range(len(json_df["features"])):
                target_text = json_df['features'][i]["properties"]["text"]
                target_pts = json_df['features'][i]["geometry"]["coordinates"]
            
                clean_txt = []
                if type(target_text) == str:
                    for t in range(len(target_text)):
                        txt = target_text[t]
                        if txt.isalpha():
                            clean_txt.append(txt)
                            
                    temp_label = ''.join([str(item) for item in clean_txt])
                    if len(temp_label) != 0:
                        target_text = temp_label
                        
                        process = re.findall('[A-Z][^A-Z]*', target_text)
                        if all(c.isupper() for c in process) or len(process) == 1: 
                            
                            if type(target_text) == str and any(c.isalpha() for c in target_text): 
                                inputs = target_text.upper()
                                q1 = {"query": {"match": {"message": {"query": f"{inputs}"} }}} # edist 0
                                test = es.search(index="usa_name_count", body=q1, size=100)["hits"]["hits"] 

                            edist = []
                            edist_update = []
                            
                            edd_min_find = 0
                            min_candidates = False
                            
                            if test != 'NaN':
                                for tt in range(len(test)):
                                    if 'name' in test[tt]['_source']:
                                        candidate = test[tt]['_source']['name']
                                        edist.append(candidate)
                            
                                for e in range(len(edist)):
                                    edd = nltk.edit_distance(inputs.upper(), edist[e].upper())

                                    if edd == 0:
                                        edist_update.append(edist[e])
                                        min_candidates = edist[e]
                                        edd_min_find = 1
                            
                            # edd 1
                            if edd_min_find != 1:
                                q2 = {"query": {"match": {"message": {"query": f"{inputs}", "fuzziness": "1"} }}} 
                                test = es.search(index="usa_name_count", body=q2, size=100)["hits"]["hits"]
                                
                                edist = []
                                edist_count = []
                                edist_update = []
                                edist_count_update = []

                                if test != 'NaN':
                                    for tt in range(len(test)):
                                        if 'name' in test[tt]['_source']:
                                            candidate = test[tt]['_source']['message']
                                            cand = candidate.split(',')[0]
                                            count = candidate.split(',')[1]
                                            edist.append(cand)
                                            edist_count.append(count)
                                                                            
                                    for e in range(len(edist)):
                                        edd = nltk.edit_distance(inputs.upper(), edist[e].upper())

                                        if edd == 1:
                                            edist_update.append(edist[e])
                                            edist_count_update.append(edist_count[e])
                                            
                                    if len(edist_update) != 0:
                                        index = edist_count_update.index(max(edist_count_update))
                                        min_candidates = edist_update[index]
                                        edd_min_find = 1
                                
                            # edd 2
                            if edd_min_find != 1:
                                q2 = {"query": {"match": {"message": {"query": f"{inputs}", "fuzziness": "2"} }}} 
                                test = es.search(index="usa_name_count", body=q2, size=100)["hits"]["hits"]
                                
                                edist = []
                                edist_count = []
                                edist_update = []
                                edist_count_update = []

                                if test != 'NaN':
                                    for tt in range(len(test)):
                                        if 'name' in test[tt]['_source']:
                                            candidate = test[tt]['_source']['message']
                                            cand = candidate.split(',')[0]
                                            count = candidate.split(',')[1]
                                            edist.append(cand)
                                            edist_count.append(count)
                                                                            
                                    for e in range(len(edist)):
                                        edd = nltk.edit_distance(inputs.upper(), edist[e].upper())

                                        if edd == 2:
                                            edist_update.append(edist[e])
                                            edist_count_update.append(edist_count[e])
                                            
                                    if len(edist_update) != 0:
                                        index = edist_count_update.index(max(edist_count_update))
                                        min_candidates = edist_update[index]
                                        edd_min_find = 1
                            
                            if edd_min_find != 1:
                                min_candidates = False
                            
                            if min_candidates != False:
                                json_df['features'][i]["properties"]["postocr_label"] = min_candidates
                            else:
                                json_df['features'][i]["properties"]["postocr_label"] = target_text

                    else:
                        # only numeric pred_text
                        json_df['features'][i]["properties"]["postocr_label"] = target_text

                else:
                    json_df['features'][i]["properties"]["postocr_label"] = target_text

            # Save
            with open(output_geojson, 'w') as json_file:
                json.dump(json_df, json_file)
            
            # print(f'Done: {map_name_output}')
            logging.info('Done generating post-OCR geojson for %s', map_name_output)


def main(args):
    query(args)


if __name__ == '__main__':
    
   
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_geojson_dir', type=str, default='/data2/rumsey_output/test2/', 
                        help='input dir for post-OCR module (= the output of M4) /crop_MN/output_stitch/')
    parser.add_argument('--out_geojson_dir', type=str, default='/data2/rumsey_output/out/',
                        help='post-OCR result')

    args = parser.parse_args()
    print(args)
    
    # if not os.path.isdir(args.out_geojson_dir):
    #     os.makedirs(args.out_geojson_dir)
    #     print('created dir',args.out_geojson_dir)
    
    main(args)