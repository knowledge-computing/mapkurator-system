import os
import glob
import pandas as pd 
import numpy as np
import argparse
from geojson import Polygon, Feature, FeatureCollection, dump
import logging
import pdb

logging.basicConfig(level=logging.INFO)
pd.options.mode.chained_assignment = None

def concatenate_and_convert_to_geojson(args):
    map_subdir = args.input_dir
    output_geojson = args.output_geojson
    shift_size = args.shift_size
    eval_bool = args.eval_only

    file_list = glob.glob(map_subdir + '/*.json')
    file_list = sorted(file_list)
    if len(file_list) == 0:
        logging.warning('No files found for %s' % map_subdir)
    
    map_data = []
    for file_path in file_list:
        patch_index_h, patch_index_w = os.path.basename(file_path).split('.')[0].split('_')
        patch_index_h = int(patch_index_h[1:])
        patch_index_w = int(patch_index_w[1:])
        try:
            df = pd.read_json(file_path)
        except pd.errors.EmptyDataError:
            logging.warning('%s is empty. Skipping.' % file_path)
            

        for index, line_data in df.iterrows():
            df['polygon_x'][index] = np.array(df['polygon_x'][index]) + shift_size * patch_index_w
            df['polygon_y'][index] = np.array(df['polygon_y'][index]) + shift_size * patch_index_h
        map_data.append(df)

    map_df = pd.concat(map_data)

    features = []
    for index, line_data in map_df.iterrows():
        polygon_x, polygon_y = list(line_data['polygon_x']), list(line_data['polygon_y'])
        
        if eval_bool ==  False: 
            # y is kept to be positive.  Needs to be negative for QGIS visualization
            # For flip coordinates: [x,-y] for x,y in zip(polygon_x, polygon_y), 
            # To form a closed loop polygon: [polygon_x[0], -polygon_y[0]], otherwise QGIS can not display the polygon
            polygon = Polygon([[[x,-y] for x,y in zip(polygon_x, polygon_y)]+[[polygon_x[0], -polygon_y[0]]]])
        else:
            polygon = Polygon([[[x,y] for x,y in zip(polygon_x, polygon_y)]+[[polygon_x[0], polygon_y[0]]]])
            
        text = line_data['text']
        score = line_data['score']
        features.append(Feature(geometry = polygon, properties={"text": text, "score": score} ))

    feature_collection = FeatureCollection(features)
    # with open(os.path.join(output_dir, map_subdir +'.geojson'), 'w') as f:
    #     dump(feature_collection, f)
    with open(output_geojson, 'w', encoding='utf8') as f:
        dump(feature_collection, f, ensure_ascii=False)
    
    logging.info('Done generating geojson (img coord) for %s', map_subdir)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, default='data/100_maps_crop_abc/0063014',
                        help='path to input json path.')
    
    parser.add_argument('--output_geojson', type=str, default='data/100_maps_geojson_abc/0063014.geojson',
                        help='path to output geojson path')

    parser.add_argument('--shift_size', type=int, default = 1000,
                        help='image patch size and shift size.')
    
    # This can not be of string type. Otherwise it will be interpreted to True all the time.
    parser.add_argument('--eval_only', default = False, action='store_true',
                        help='keep positive coordinate')
   
    args = parser.parse_args()
    print(args)

    concatenate_and_convert_to_geojson(args)





