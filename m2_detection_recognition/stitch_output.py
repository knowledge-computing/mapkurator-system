import os
import glob
import pandas as pd 
import numpy as np
from geojson import Polygon, Feature, FeatureCollection, dump
import pdb

input_dir = '../data/100_maps_crop_outabc/'
output_dir = '../data/100_maps_outabc/'
shift_size = 1000

if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

pd.options.mode.chained_assignment = None

def concatenate_and_convert_to_geojson(input_dir):

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
    concatenate_and_convert_to_geojson(input_dir)

# point = pts[int(image[:-4])].split(',')
# point[1::2] = [str(-1*float(y)) for y in point[1::2]]
# point = Polygon([list(map(tuple, np.array(point, dtype=np.float).reshape(-1,2)))])

# features.append(Feature(geometry=point, properties={"name": name, "confidence_score": score, "averaged_confidence_score": average_score}))

# print(f'{opt.image_folder+image:25s}\t{name:25s}\t')

# feature_collection = FeatureCollection(features)
# with open("../david-rumsey-exp/mapkurator-"+ str(opt.image_folder).split("/")[4] +'.geojson', 'w+') as log:
# dump(feature_collection, log)