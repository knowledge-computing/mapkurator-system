#-*-coding utf-8-*-
import logging 
import requests
import json
import argparse
import http.client as http_client
import nltk
import re
import glob
import os

import elasticsearch
import elasticsearch.helpers

# set the debug level
http_client.HTTPConnection.debuglevel = 1
logging.basicConfig(level=logging.INFO)
# warnings.filterwarnings("ignore")
        
headers = {
    'Content-Type': 'application/json',
}

es = elasticsearch.Elasticsearch([{'host': "127.0.0.1", 'port': 9200}], timeout=1000)


def query(args):
    """ Query candidates and save them as 'postocr_label' """

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
                                # edist 0
                                inputs = "minnesota"
                                fff = 1
                                es_query = {'query': {'fuzzy': {'name': {'value': inputs, 'fuzziness': fff}}}}
                                
                                try:
                                    es_results = elasticsearch.helpers.scan(es, index="osm-voca", preserve_order=True, query=es_query)
                                except elasticsearch.ElasticsearchException as es_error:
                                    print(es_error)
                                    continue
                                # for item in es_results:
                                #     print('here1:', item['_source']['name'])
                                #     print('here1:', item['_source']['count'])
                                #     print('here1: ', item['_source']['message'])

                                test2 = [item['_source'] for item in es_results if item["_source"]['name'] is not None]
                                for i in range(len(test2)):
                                    line = test2[i]
                                    print(line['message'])
                                    if 'name' in test2[i]:
                                        print("yes")
                                        print(line['name'])
                                    print(test2[i])
                                print(alejsj)

                                # test3 = []
                                # for src in es_results:
                                #     print("this 2")
                                #     print(src['_source'])
                                #     test3.append(src['_source'])

                                print(test2)
                                print(len(test2))
                                print("this: ", test3)
                                print(len(test3))
                                print(akakakak)

                                print('test2: ', test2)
                                print('test2: ', test2[0]['message'])
                                print("-----")
                                q1 = '{"track_total_hits": true, "query": {"fuzzy": {"name": {"value": "'+ inputs +'", "fuzziness": "'+ str(0) +'"}}}}' 
                                resp = requests.get(f'http://localhost:9200/osm-voca/_search?', \
                                            data=q1.encode("utf-8"), \
                                            headers = headers)
                                resp_json = json.loads(resp.text)
                                test = resp_json["hits"]["hits"]
                                print('test2: ', test)
                                print('test2: ', test['message'])
                                print(akakak)
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
                                # edist 1
                                q2 = '{"query": {"fuzzy": {"name": {"value": "'+ inputs +'", "fuzziness": "1"}}}}' 
                                resp = requests.get(f'http://localhost:9200/osm-voca/_search?', \
                                            data=q2.encode("utf-8"), \
                                            headers = headers)
                                resp_json = json.loads(resp.text)
                                test = resp_json["hits"]["hits"]
                                
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
                                # edist 2
                                q3 = '{"query": {"fuzzy": {"name": {"value": "'+ inputs +'", "fuzziness": "2"}}}}' 
                                resp = requests.get(f'http://localhost:9200/osm-voca/_search?', \
                                            data=q3.encode("utf-8"), \
                                            headers = headers)
                                resp_json = json.loads(resp.text)
                                test = resp_json["hits"]["hits"]
                                
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
                                json_df['features'][i]["properties"]["postocr_label"] = str(min_candidates)
                            else:
                                json_df['features'][i]["properties"]["postocr_label"] = str(target_text)
                        
                        else: # added
                            json_df['features'][i]["properties"]["postocr_label"] = str(target_text)
                    
                    else:
                        # only numeric pred_text
                        json_df['features'][i]["properties"]["postocr_label"] = str(target_text)

                else:
                    json_df['features'][i]["properties"]["postocr_label"] = str(target_text)
            
            # Save
            with open(output_geojson, 'w') as json_file:
                json.dump(json_df, json_file, ensure_ascii=False)
        
            logging.info('Done generating post-OCR geojson for %s', map_name_output)


def main(args):
    query(args)


if __name__ == '__main__':
    
   
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_geojson_dir', type=str, default='/data4/leeje/rumsey_output/sample_rumsey/geocoord/Russian/5763001.geojson', 
                        help='input dir for post-OCR module (= the output of M4) /crop_MN/output_stitch/')
    parser.add_argument('--out_geojson_dir', type=str, default='/data4/leeje/rumsey_output/sample_rumsey/postocr_linking/test',
                        help='post-OCR result')

    args = parser.parse_args()
    print(args)
    
    # if not os.path.isdir(args.out_geojson_dir):
    #     os.makedirs(args.out_geojson_dir)
    #     print('created dir',args.out_geojson_dir)
    
    main(args)