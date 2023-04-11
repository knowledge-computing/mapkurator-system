import glob
import os
import json
import argparse

import elasticsearch
import elasticsearch.helpers

from post_ocr import lexical_search_query


es = elasticsearch.Elasticsearch([{'host': "127.0.0.1", 'port': 9200}], timeout=1000)

def main(args):

    input_dir = args.input_geojson_file
    output_geojson = args.out_geojson_dir

    map_name_output = input_dir.split('/')[-1]

    with open(input_dir) as json_file: 
        json_df = json.load(json_file)

        result_dict = dict()
        if json_df != {}:  
            query_result = []
            for i in range(len(json_df["features"])):
                target_text = json_df['features'][i]["properties"]["text"].lower()
                query_text = lexical_search_query(target_text, es)
                result_dict[target_text] = query_text
        
        for feature_data in json_df["features"]:
            feature_data["properties"]["postocr_label"] = result_dict[str(feature_data["properties"]["text"]).lower()]

    with open(os.path.join(output_geojson, map_name_output), 'w') as json_file:
        json.dump(json_df, json_file, ensure_ascii=False)


if __name__ == '__main__':
    
   
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_geojson_file', type=str, default='/data4/leeje/rumsey_output/sample_rumsey/geocoord/Russian/5763001.geojson', 
                        help='')
    parser.add_argument('--out_geojson_dir', type=str, default='/data4/leeje/rumsey_output/sample_rumsey/postocr_linking/test/5763001.geojson',
                        help='post-OCR result')

    args = parser.parse_args()
    print(args)
    
    main(args)
