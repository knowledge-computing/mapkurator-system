import os
import argparse
import logging
import ast

import pandas as pd
import numpy as np
import geojson
import os

logging.basicConfig(level=logging.INFO)


def main(args):
    geojson_file = args.in_geojson_file
    output_dir = args.out_geojson_dir

    sample_map_df = pd.read_csv(args.sample_map_path, dtype={'image_no': str})
    sample_map_df['image_no'] = sample_map_df['image_no'].str.replace('.1.jp2', '', regex=False).str.replace('.jp2', '', regex=False)
    sample_map_df['image_no'] = sample_map_df['image_no'].apply(lambda x: x[:-2] if x[-2:] == '.1' else x)
    
    geojson_filename_id = geojson_file.split(".")[0].split("/")[-1]

    if not os.path.isdir(os.path.join(output_dir, "tmp/")):
        os.makedirs(os.path.join(output_dir, "tmp/"))

    row = sample_map_df[sample_map_df['image_no'] == geojson_filename_id]
    if not row.empty:
        gcps = ast.literal_eval(row.iloc[0]['gcps'])
        gcp_str = ''
        for gcp in gcps:
            lng, lat = gcp['location']
            x, y = gcp['pixel']
            gcp_str += '-gcp ' + str(x) + ' ' + str(y) + ' ' + str(lng) + ' ' + str(lat) + ' '

        transform_method = row.iloc[0]['transformation_method']
        assert transform_method in ['affine', 'polynomial', 'tps']

        # minus in y
        with open(geojson_file) as img_geojson:
            try:
                img_data = geojson.load(img_geojson)
            except json.decoder.JSONDecodeError:
                if os.stat(geojson_file).st_size == 0:
                    with open(os.path.join(output_dir, geojson_filename_id + '.geojson'), 'w') as fp:
                        pass
                    logging.info('Done generating empty geocoord geojson for %s', geojson_file)
                else:
                    logging.info('JSONDecodeError %s', geojson_file)
                return

            for img_feature in img_data['features']:
                arr = np.array(img_feature['geometry']['coordinates'])
                img_feature['properties']['img_coordinates'] = np.array(arr).reshape(-1, 2).tolist()

                arr[:, :, 1] *= -1
                img_feature['geometry']['coordinates'] = arr.tolist()

        with open(os.path.join(os.path.join(output_dir, "tmp/"), geojson_filename_id + '.geojson'), 'w', encoding='utf8') as geocoord_geojson:
            geojson.dump(img_data, geocoord_geojson, ensure_ascii=False)

        input = '"' + output_dir + "/tmp/" + geojson_filename_id + '.geojson"'
        output = '"' + output_dir + "/" + geojson_filename_id + '.geojson"'

        if transform_method == 'affine':
            gecoord_convert_command = 'ogr2ogr -f "GeoJSON" ' + output + " " + input + ' -order 1 -s_srs epsg:4326 -t_srs epsg:3857 -skipfailures ' + gcp_str

        elif transform_method == 'polynomial':
            gecoord_convert_command = 'ogr2ogr -f "GeoJSON" ' + output + " " + input + ' -order 2 -s_srs epsg:4326 -t_srs epsg:3857 -skipfailures ' + gcp_str

        elif transform_method == 'tps':
            gecoord_convert_command = 'ogr2ogr -f "GeoJSON" ' + output + " " + input + ' -tps -s_srs epsg:4326 -t_srs epsg:3857 -skipfailures ' + gcp_str

        else:
            raise NotImplementedError

        ret_value = os.system(gecoord_convert_command)
        if os.path.exists(os.path.join(os.path.join(output_dir, "tmp/"), geojson_filename_id + '.geojson')):
            os.remove(os.path.join(os.path.join(output_dir, "tmp/"), geojson_filename_id + '.geojson'))

        if ret_value != 0:
            logging.info('Failed generating geocoord geojson for %s', geojson_file)
        else:
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
