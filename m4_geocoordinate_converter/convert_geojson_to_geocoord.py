import os
import argparse
import ast

import pandas as pd
import numpy as np

from rasterio.control import GroundControlPoint
from rasterio.transform import from_gcps

import geojson


def main(args):

    sample_map_df = pd.read_csv(args.sample_map_path, dtype={'external_id': str})
    geojson_files = os.listdir(args.in_geojson_dir)

    sample_map_df['external_id'] = sample_map_df['external_id'].str.strip("'").str.replace('.', '')

    for geojson_file in geojson_files:
        row = sample_map_df[sample_map_df['external_id']==geojson_file.split(".")[0]]
        if not row.empty and row.iloc[0]['transformation_method']=='affine':
            gcps = ast.literal_eval(row.iloc[0]['gcps'])

            control_point = []
            for gcp in gcps:
                row, col = gcp['pixel']
                lng, lat = gcp['location']
                control_point.append(GroundControlPoint(float(col), float(row), float(lng), float(lat)))
                # print(float(col), float(row), float(lng), float(lat))
            transform = from_gcps(control_point)

            with open(args.in_geojson_dir+geojson_file) as f:
                data = geojson.load(f)

            for feature_data in data['features']:
                pts = np.array(feature_data['geometry']['coordinates'], dtype=np.int32).reshape(-1, 2)
                pts[:, 1] = pts[:, 1]*-1
                transformed_pts = np.apply_along_axis(lambda x: transform * x, axis=1, arr=pts)
                feature_data['geometry']['coordinates'] = [transformed_pts.tolist()]

            with open(args.out_geojson_dir+geojson_file, 'w') as output_geojson:
                geojson.dump(data, output_geojson)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample_map_path', type=str, default='data/initial_US_100_maps.csv',
                        help='path to sample map csv, which contains gcps info')
    parser.add_argument('--in_geojson_dir', type=str, default='data/100_maps_geojson_abc/',
                        help='input dir for results of M2')
    parser.add_argument('--out_geojson_dir', type=str, default='data/100_maps_geojson_abc_geocoord/',
                        help='output dir for converted geojson files')

    args = parser.parse_args()

    main(args)
