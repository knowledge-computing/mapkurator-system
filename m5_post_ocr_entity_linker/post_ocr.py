import logging
import requests
import json
import http.client as http_client
import nltk
import re

# set the debug level
logging.getLogger("requests").setLevel(logging.WARNING)
        
headers = {
    'Content-Type': 'application/json',
}


def scrolling(inputs, resp, fuzziness):
    # Added
    if resp.status_code == 200:
        resp_json = json.loads(resp.text)
        n_value = resp_json["hits"]["total"]["value"]
        count = 0

        if n_value > 10:
            # Search memory control
            if n_value > 10000:
                json_size_body = '{"max_result_window":'+ str(n_value + 1) +'}'

                resp_setting = requests.put(f'http://localhost:9200/osm-voca/_settings', \
                        data=json_size_body, \
                        headers = headers)
                scroll_time = 60
            else: 
                # Back to the default due to the search capability
                json_size_body = '{"max_result_window": 10000 }'

                resp_setting = requests.put(f'http://localhost:9200/osm-voca/_settings', \
                        data=json_size_body, \
                        headers = headers)
                scroll_time = 30
            
            # while count != n_value:
            # Create Scroll ID and Search all results
            # Fuzzy = 0, 1, 2
            try:
                q1 = '{"size":'+ str(n_value) +', "query": {"fuzzy": {"name": {"value": "'+ inputs +'", "fuzziness": "'+ str(fuzziness) +'"}}}}' 
                resp_page_search = requests.get(f'http://localhost:9200/osm-voca/_search?&scroll={scroll_time}m', \
                    data=q1.encode("utf-8"), \
                    headers = headers)

                if resp_page_search.status_code == 200:
                    resp_json = json.loads(resp_page_search.text)
                    s_id = resp_json["_scroll_id"]

            except Exception as e:
                print(e.message)

        else:
            s_id = 0

        return s_id, resp_json

def remove_sid(s_id):
    # Remove the scroll ID
    # To avoid elasticsearch memory leakage
    try:
        json_close_page = '{"scroll_id": "'+ s_id +'"}'
        resp_page = requests.delete(f'http://localhost:9200/_search/scroll', \
                data=json_close_page, \
                headers = headers)
        
    except Exception as e:
        print(e.message)


def lexical_search_query(target_text):
    """ Query candidates and save them as 'postocr_label' """

    clean_txt = []
    if type(target_text) == str:
        if any(char.isdigit() for char in target_text) == False:
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
                        fuzziness = 0
                        inputs = target_text.lower()
                        q1 = '{"track_total_hits": true, "query": {"fuzzy": {"name": {"value": "'+ inputs +'", "fuzziness": "'+ str(fuzziness) +'"}}}}' 
                        resp = requests.get(f'http://localhost:9200/osm-voca/_search?', \
                                    data=q1.encode("utf-8"), \
                                    headers = headers)
                        s_id, resp_json = scrolling(inputs, resp, fuzziness)
                        resp_json = json.loads(resp.text)
                        test = resp_json["hits"]["hits"]

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
                        
                    if s_id != 0:
                        remove_sid(s_id)

                    # edd 1
                    if edd_min_find != 1:
                        # edist 1
                        fuzziness = 1
                        q2 = '{"track_total_hits": true, "query": {"fuzzy": {"name": {"value": "'+ inputs +'", "fuzziness": "'+ str(fuzziness) +'"}}}}' 
                        resp = requests.get(f'http://localhost:9200/osm-voca/_search?', \
                                    data=q2.encode("utf-8"), \
                                    headers = headers)
                        s_id, resp_json = scrolling(inputs, resp, fuzziness)
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

                        if s_id != 0:
                            remove_sid(s_id)

                    # edd 2
                    if edd_min_find != 1:
                        # edist 2
                        fuzziness = 2
                        q3 = '{"track_total_hits": true, "query": {"fuzzy": {"name": {"value": "'+ inputs +'", "fuzziness": "'+ str(fuzziness) +'"}}}}' 
                        resp = requests.get(f'http://localhost:9200/osm-voca/_search?', \
                                    data=q3.encode("utf-8"), \
                                    headers = headers)
                        s_id, resp_json = scrolling(inputs, resp, fuzziness)
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

                        if s_id != 0:
                            remove_sid(s_id)

                    if edd_min_find != 1:
                        min_candidates = False


                    if min_candidates != False:
                        return str(min_candidates)
                    else:
                        return str(target_text)

                else: # added
                    return str(target_text)

            else:
                # only numeric pred_text
                return str(target_text)
        else:
            # Combination of 140D -> 140D
            return str(target_text)
    else:
        return str(target_text)