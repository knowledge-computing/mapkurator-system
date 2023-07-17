import logging
import requests
import json
import http.client as http_client
import nltk
import re

import elasticsearch
import elasticsearch.helpers


def lexical_search_query(target_text, es):
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
                        q1 = {'query': {'fuzzy': {'name': {'value': inputs, 'fuzziness': 0}}}}
                        try:
                            es_results = elasticsearch.helpers.scan(es, index="osm-voca", preserve_order=True, query=q1)
                        except elasticsearch.ElasticsearchException as es_error:
                            print(es_error)

                        test = [item['_source'] for item in es_results if item["_source"]['name'] is not None]
                        

                    edist = []
                    edist_update = []

                    edd_min_find = 0
                    min_candidates = False

                    if test != 'NaN':
                        for tt in range(len(test)):
                            if 'name' in test[tt]:
                                candidate = test[tt]['name']
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
                        fuzziness = 1

                        q2 = {'query': {'fuzzy': {'name': {'value': inputs, 'fuzziness': fuzziness}}}}
                        try:
                            es_results = elasticsearch.helpers.scan(es, index="osm-voca", preserve_order=True, query=q2)
                        except elasticsearch.ElasticsearchException as es_error:
                            print(es_error)

                        test = [item['_source'] for item in es_results if item["_source"]['name'] is not None]


                        edist = []
                        edist_count = []
                        edist_update = []
                        edist_count_update = []

                        if test != 'NaN':
                            for tt in range(len(test)):
                                if 'name' in test[tt]:
                                    candidate = test[tt]['message']
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
                        fuzziness = 2
                        q3 = {'query': {'fuzzy': {'name': {'value': inputs, 'fuzziness': fuzziness}}}}
                        try:
                            es_results = elasticsearch.helpers.scan(es, index="osm-voca", preserve_order=True, query=q3)
                        except elasticsearch.ElasticsearchException as es_error:
                            print(es_error)

                        test = [item['_source'] for item in es_results if item["_source"]['name'] is not None]

                        edist = []
                        edist_count = []
                        edist_update = []
                        edist_count_update = []

                        if test != 'NaN':
                            for tt in range(len(test)):
                                if 'name' in test[tt]:
                                    candidate = test[tt]['message']
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