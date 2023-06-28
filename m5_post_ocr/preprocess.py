from elasticsearch import Elasticsearch
import logging
import requests
import json

import http.client as http_client

import pandas as pd
import string
import emoji
import time
import string

import glob
import os 



def read_name():
    http_client.HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


    #Popularity Count
    headers = {
        'Content-Type': 'application/json',
    }

    json_body = '{"track_total_hits": true}'

    resp = requests.get(f'http://localhost:9200/osm/_search?&pretty=true', \
                data=json_body, \
                headers = headers)
    resp_json = json.loads(resp.text)
    total_value = resp_json["hits"]["total"]["value"] 


    # Initialize
    json_body_page = '{"track_total_hits": true, "size": 10000, "sort": [{"ogc_fid": {"order" : "desc" }}]}'
    resp_page = requests.post(f'http://localhost:9200/osm/_search?', \
                data=json_body_page, \
                headers = headers)
    resp_page_json = json.loads(resp_page.text)
  
    name_list = []

    st = []
    for h in range(len(resp_page_json["hits"]["hits"])):
        st = resp_page_json["hits"]["hits"][h]["sort"]
        text = resp_page_json["hits"]["hits"][h]["_source"]["name"]
        token_list = text.split(" ")
        for t in range(len(token_list)):
            name_list.append(token_list[t].lower())
        
    n_val = len(resp_page_json["hits"]["hits"])
    st_list = [st[0]]
    error_track = []

    # Iterate over pages
    while n_val != total_value:

        try: #osm_id.keyword
            json_body_page2 = '{"track_total_hits": true, "size": 10000, "sort": [{"ogc_fid": {"order" : "desc" }}], "search_after": ['+str(st[0])+']}'
            resp_page2 = requests.get(f'http://localhost:9200/osm/_search?', \
                        data=json_body_page2, \
                        headers = headers)
            resp_page_json2 = json.loads(resp_page2.text)

            for h in range(len(resp_page_json2["hits"]["hits"])):
                st = resp_page_json2["hits"]["hits"][h]["sort"]
                text = resp_page_json2["hits"]["hits"][h]["_source"]["name"]
                token_list = text.split(" ")
                for t in range(len(token_list)):
                    name_list.append(token_list[t].lower())

            n_val += len(resp_page_json2["hits"]["hits"])
            st_list.append(st[0])
            print(f'n_val: {n_val} done!')

        except Exception as e:
            print(e.message)
            error_track.append(str(st[0])) 

            with open('error_id.txt', 'w') as fp:
                for item in error_track:
                    fp.write("%s\n" % item)
                print('Done')

            with open('name_mid.txt', 'w') as fp:
                for item in name_list:
                    fp.write("%s\n" % item)
                print('Done')
            
            with open('last_sort_id.txt', 'w') as fp:
                for item in st_list:
                    fp.write("%s\n" % item)
                print('Done')

    with open('name.txt', 'w') as fp:
        for item in name_list:
            fp.write("%s\n" % item)
        print('Done')

    with open('name_set.txt', 'w') as fp:
        name_set = list(set(name_list))
        for item in name_set:
            fp.write("%s\n" % item)
        print('Done')



def counting():
    input_txt = "name.txt"

    if os.path.exists(input_txt):

        punc = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
        start2 = time.time()
        set_lst2 = []
        with open(input_txt) as file:
            for item in file:
                name = emoji.replace_emoji(item.strip(), '') #filter out emoji
                name = name.translate(str.maketrans('', '', string.punctuation))
                if len(name) > 0:
                    set_lst2.append(name.upper())

        end2 = time.time()
        start = time.time()

        dic = {}
        count = 0
        
        for word in set_lst2:
            count += 1
            if word in dic:
                dic[word] += 1
            else:
                dic[word] = 1

        end = time.time()

        print(end - start)
        print(end2 - start2)
        dff = pd.DataFrame.from_dict([dic]).T

        dff.reset_index(inplace=True)
        dff = dff.rename(columns = {'index':'name', '0': 'count'})
        dff.to_csv("out.csv", index=False)


if __name__ == '__main__':
    read_name()
    counting()
