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

logging.basicConfig(level=logging.INFO)

def db_connect():
    """Elasticsearch Connection on Sansa"""
    
    load_dotenv()
    
    DB_HOST = os.getenv("DB_HOST")
    USER_NAME = os.getenv("DB_USERNAME")
    PASSWORD = os.getenv("DB_PASSWORD")

    es = Elasticsearch([DB_HOST], connection_class=RequestsHttpConnection, http_auth=(USER_NAME, PASSWORD), verify_certs=False)
    
    return es



def find_min_edist(target, candidates):
    """Helper func: Compute edist and save the identical edist (the smallest) candidates"""
    
    edd_list = []
    pop_list = []

    for i in candidates:
        compare = i.split(',')[0]
        edd = nltk.edit_distance(target.upper(), compare.upper())
        edd_list.append(edd)
    
    min_edd = min(edd_list)
    
    min_candidates = [candi for j, candi in enumerate(candidates) if edd_list[j] == min_edd]

    # Pick the most popular one if there are multiple same edist candidate existed
    if len(min_candidates) > 1:
        
        for k in min_candidates:
            
            ipop = k.split(',')[-1]
            if ipop.isnumeric() ==True:
                pop_list.append(ipop)
        
        pop_list = list(map(int, pop_list))
        pop_idx = pop_list.index(max(pop_list))
        pick = min_candidates[pop_idx].split(',')[0]
        return pick
    
    else:
        return min_candidates[0].split(',')[0]
    

def query(args):
    """ Query candidates and save them as 'postocr_label' """
    
    es = db_connect()

    
    input_dir = args.in_geojson_dir
    output_geojson = args.out_geojson_dir
    
    file_list = glob.glob(input_dir + '/*.geojson')
    file_list = sorted(file_list)
    
    if len(file_list) == 0:
        logging.warning('No files found for %s' % input_dir)

    for file_path in file_list:
        map_name = file_path.split('.')[0]
        # print(map_name)
        with open(file_path) as json_file:
            json_df = json.load(json_file)

            if json_df != {}:  
                query_result = []
                for i in range(len(json_df["features"])):
                    target_text = json_df['features'][i]["properties"]["text"]
                    target_pts = json_df['features'][i]["geometry"]["coordinates"]
                
                    clean_txt = []
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
                                q1 = {"query": {"match": {"message": {"query": f"{inputs}", "fuzziness": "AUTO:0,7"} }}} # edist 0, 1, 2
                                test = es.search(index="usa_namecount", body=q1, size=100)["hits"]["hits"] 
                            else:
                                test = 'NaN'

                            edist = []
                            if test != 'NaN':
                                for tt in range(len(test)):
                                    if 'name' in test[tt]['_source']:
                                        # candidate = test[tt]['_source']['name']
                                        candidate = test[tt]['_source']['message']
                                        edist.append(candidate)
                                    else:
                                        edist.append('NaN')
                            else:
                                edist.append('NaN')
                            edist = list(set(edist))

                            if type(target_text) == str and any(c.isalpha() for c in target_text) and len(edist)!=0: 
                                min_candidates = find_min_edist(target_text, edist)
                            else:
                                min_candidates = False
                            
                        else: 
                            min_candidates = False
                            target_text = ' '.join(process)
                            
                        if min_candidates != False:
                            json_df['features'][i]["properties"]["postocr_label"] = min_candidates
                        else:
                            json_df['features'][i]["properties"]["postocr_label"] = target_text

                    else:
                        # only numeric pred_text
                        json_df['features'][i]["properties"]["postocr_label"] = target_text
                # Save
                map_name_output = map_name.split('/')[-1]
                with open(output_geojson +'/'+ map_name_output + '.geojson', 'w') as json_file:
                    json.dump(json_df, json_file)
                
                # print(f'Done: {map_name_output}.geojson')
                logging.info('Done generating post-OCR geojson for %s', map_name_output)
                    

def main(args):
    query(args)


if __name__ == '__main__':
    
   
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_geojson_dir', type=str, default='file/', 
                        help='input dir for post-OCR module (= the output of M4) /crop_MN/output_stitch/')
    parser.add_argument('--out_geojson_dir', type=str, default='out/',
                        help='post-OCR result')
    
    args = parser.parse_args()
    print(args)
    
    # if not os.path.isdir(args.out_geojson_dir):
    #     os.makedirs(args.out_geojson_dir)
    #     print('created dir',args.out_geojson_dir)
    
    main(args)