import os
import argparse
import logging
import ast

import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO)

def main(args):

    geojson_file = args.in_geojson_file
    output_dir = args.out_geojson_dir

    sample_map_df = pd.read_csv(args.sample_map_path, dtype={'external_id': str})
    sample_map_df['external_id'] = sample_map_df['external_id'].str.strip("'").str.replace('.', '', regex=True)
    geojson_filename_id = geojson_file.split(".")[0].split("/")[-1]

    row = sample_map_df[sample_map_df['external_id'] == geojson_filename_id]
    if not row.empty:
        gcps = ast.literal_eval(row.iloc[0]['gcps'])
        gcp_str = ''
        for gcp in gcps:
            lng, lat = gcp['location']
            x, y = gcp['pixel']
            gcp_str += '-gcp ' + str(x) + ' ' + str(y) + ' ' + str(lng) + ' ' + str(lat) + ' '

        transform_method = row.iloc[0]['transformation_method']
        assert transform_method in ['affine', 'polynomial', 'tps']

        output = '"' + output_dir + geojson_filename_id + '.geojson"'
        input = '"' + geojson_file + '"'

        if transform_method == 'affine':
            gecoord_convert_command = 'ogr2ogr -f "GeoJSON" ' + output + " " + input + ' -order 1 ' + gcp_str

        elif transform_method == 'polynomial':
            gecoord_convert_command = 'ogr2ogr -f "GeoJSON" ' + output + " " + input + ' -order 2 ' + gcp_str

        elif transform_method == 'tps':
            gecoord_convert_command = 'ogr2ogr -f "GeoJSON" ' + output + " " + input + ' -tps ' + gcp_str

        else:
            raise NotImplementedError

        os.system(gecoord_convert_command)
        logging.info('Done generating geocoord geojson for %s', geojson_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample_map_path', type=str, default='data/initial_US_100_maps.csv',
                        help='path to sample map csv, which contains gcps info')
    parser.add_argument('--in_geojson_file', type=str,
                        help='input geojson file; results of M2')
    parser.add_argument('--out_geojson_dir', type=str, default='data/100_maps_geojson_abc_geocoord/',
                        help='output dir for converted geojson files')

    args = parser.parse_args()

    main(args)
