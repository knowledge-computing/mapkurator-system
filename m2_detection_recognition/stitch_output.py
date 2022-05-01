import os
import glob
import pandas as pd 
import numpy as np
import argparse
from geojson import Polygon, Feature, FeatureCollection, dump
import pdb

pd.options.mode.chained_assignment = None

def concatenate_and_convert_to_geojson(args):
    input_dir = args.input_dir
    output_dir = args.output_dir
    shift_size = args.shift_size

    map_subdir_list = os.listdir(input_dir)

    for map_subdir in map_subdir_list:
        file_list = glob.glob(os.path.join(input_dir, map_subdir) + '/*.json')
        file_list = sorted(file_list)
        map_data = []
        for file_path in file_list:
            patch_index_h, patch_index_w = os.path.basename(file_path).split('.')[0].split('_')
            patch_index_h = int(patch_index_h[1:])
            patch_index_w = int(patch_index_w[1:])
            try:
                df = pd.read_json(file_path)
            except pd.errors.EmptyDataError:
                print('Note: %s was empty. Skipping.' % file_path)
                continue

            #pdb.set_trace()
            for index, line_data in df.iterrows():
                df['polygon_x'][index] = np.array(df['polygon_x'][index]) + shift_size * patch_index_w
                df['polygon_y'][index] = np.array(df['polygon_y'][index]) + shift_size * patch_index_h
            map_data.append(df)

        map_df = pd.concat(map_data)

        features = []
        for index, line_data in map_df.iterrows():
            #pdb.set_trace()
            polygon_x, polygon_y = list(line_data['polygon_x']), list(line_data['polygon_y'])
            polygon = Polygon([[[x,y] for x,y in zip(polygon_x, polygon_y)]+[[polygon_x[0], polygon_y[0]]]])
            text = line_data['text']
            score = line_data['score']
            features.append(Feature(geometry = polygon, properties={"text": text, "score": score} ))

        feature_collection = FeatureCollection(features)
        with open(os.path.join(output_dir, map_subdir +'.geojson'), 'w') as f:
            dump(feature_collection, f)

if __name__ == '__main__':
    #concatenate_and_convert_to_geojson(input_dir)

    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, default='data/100_maps_crop_abc/',
                        help='path to input json path.')
    parser.add_argument('--output_dir', type=str, default='data/100_maps_geojson_abc/',
                        help='path to output geojson path')
    parser.add_argument('--shift_size', type=int, default = 1000,
                        help='image patch size and shift size.')
   
    args = parser.parse_args()
    print(args)

    concatenate_and_convert_to_geojson(args)





