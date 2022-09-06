import os
import glob
import argparse
import time
import logging
import pandas as pd
import pdb
import datetime
from PIL import Image 
from utils import get_img_path_from_external_id

logging.basicConfig(level=logging.INFO)
Image.MAX_IMAGE_PIXELS=None # allow reading huge images

'''
This Sanborn processing pipeline shares some common modules as DR processing pipeline, including cropping and text spotting. 
The unique modules are geocoding, clustering, and output geojson generation module. 
The GeoTiff conversion, Image dimension retrival, Img_to_geo coord and entity linking modules are removed.
Time usage analysis and error reason logging are removed. 
'''

def execute_command(command, if_print_command):
    t1 = time.time()

    if if_print_command:
        print(command)
    os.system(command)

    t2 = time.time()
    time_usage = t2 - t1 
    return time_usage

def get_img_dimension(img_path):
    map_img = Image.open(img_path) 
    width, height = map_img.size 

    return width, height


def run_pipeline(args):
    # -------------------------  Pass arguments -----------------------------------------
    map_kurator_system_dir = args.map_kurator_system_dir
    text_spotting_model_dir = args.text_spotting_model_dir
    # sample_map_path = args.sample_map_csv_path
    expt_name = args.expt_name
    output_folder = args.output_folder
    input_map_dir = args.input_map_dir

    module_get_dimension = args.module_get_dimension
    # module_gen_geotiff = args.module_gen_geotiff
    module_cropping = args.module_cropping
    module_text_spotting = args.module_text_spotting
    module_img_geojson = args.module_img_geojson 
    # module_geocoord_geojson = args.module_geocoord_geojson 
    # module_entity_linking = args.module_entity_linking
    module_geocoding = args.module_geocoding
    module_clustering = args.module_clustering

    spotter_option = args.spotter_option
    geocoder_option = args.geocoder_option
    api_key = args.api_key 
    user_name = args.user_name

    metadata_tsv_path = args.metadata_tsv_path

    if_print_command = args.print_command

    sid_to_jpg_dir = '/data2/rumsey_sid_to_jpg/'

    file_list = os.listdir(input_map_dir)

    file_list = [f for f in file_list if os.path.basename(f).split('.')[-1] in ['sid','jp2','png','jpg','jpeg','tiff','tif','geotiff','geotiff']]
    
    print(len(file_list))

    

    # pdb.set_trace()
    # ------------------------- Read sample map list and prepare output dir ----------------

    cropping_output_dir = os.path.join(output_folder, expt_name, 'crop/')
    spotting_output_dir = os.path.join(output_folder, expt_name,  'spotter/' + spotter_option)
    stitch_output_dir = os.path.join(output_folder, expt_name, 'stitch/' + spotter_option)
    # geojson_output_dir = os.path.join(output_folder, expt_name, 'geojson_' + spotter_option + '/')
    geocoding_output_dir = os.path.join(output_folder, expt_name, 'geocoding_suffix_' + spotter_option)
    clustering_output_dir = os.path.join(output_folder, expt_name, 'cluster_' + spotter_option + '/')
    

    # ------------------------- Image cropping  ------------------------------
    if module_cropping:
        # for index, record in sample_map_df.iterrows():
        for file_path in file_list:
            img_path = os.path.join(input_map_dir, file_path)
            print(img_path)
            # external_id = record.external_id
            # img_path = external_id_to_img_path_dict[external_id]
            
            map_name = os.path.basename(img_path).split('.')[0]
            

            os.chdir(os.path.join(map_kurator_system_dir ,'m2_detection_recognition'))
            if not os.path.isdir(cropping_output_dir):
                os.makedirs(cropping_output_dir)
            run_crop_command = 'python crop_img.py --img_path '+img_path + ' --output_dir '+ cropping_output_dir

            time_usage = execute_command(run_crop_command, if_print_command)
            # time_usage_dict[external_id]['cropping'] = time_usage

    time_cropping = time.time()
    
    # # ------------------------- Text Spotting (patch level) ------------------------------
    if module_text_spotting:
        os.chdir(text_spotting_model_dir)

        # for index, record in sample_map_df.iterrows():
        for file_path in file_list:
            map_name = os.path.basename(file_path).split('.')[0]

            map_spotting_output_dir = os.path.join(spotting_output_dir,map_name)
            if not os.path.isdir(map_spotting_output_dir):
                os.makedirs(map_spotting_output_dir)

            if spotter_option == 'abcnet':
                run_spotting_command = 'python demo/demo.py 	--config-file configs/BAText/CTW1500/attn_R_50.yaml 	--input='+ os.path.join(cropping_output_dir,map_name) + '  --output='+ map_spotting_output_dir + '   --opts MODEL.WEIGHTS ctw1500_attn_R_50.pth'
            elif spotter_option == 'testr':
                run_spotting_command = 'python demo/demo.py --output_json	--input='+ os.path.join(cropping_output_dir,map_name) + ' --output='+map_spotting_output_dir +'   --opts MODEL.WEIGHTS icdar15_testr_R_50_polygon.pth'
            else:
                raise NotImplementedError

            run_spotting_command  += ' 1> /dev/null'
            
            time_usage = execute_command(run_spotting_command, if_print_command)
            
            logging.info('Done text spotting for %s', map_name)

    time_text_spotting = time.time()
    

    # # ------------------------- Image coord geojson (map level) ------------------------------
    if module_img_geojson:
        os.chdir(os.path.join(map_kurator_system_dir ,'m3_image_geojson'))
        if not os.path.isdir(stitch_output_dir):
            os.makedirs(stitch_output_dir)

        for file_path in file_list:
            map_name = os.path.basename(file_path).split('.')[0]

            stitch_input_dir = os.path.join(spotting_output_dir, map_name)
            output_geojson = os.path.join(stitch_output_dir, map_name + '.geojson')
            
            run_stitch_command = 'python stitch_output.py --input_dir '+stitch_input_dir + ' --output_geojson ' + output_geojson
            time_usage = execute_command(run_stitch_command, if_print_command)
            # time_usage_dict[external_id]['imgcoord_geojson'] = time_usage

    time_img_geojson = time.time()

    # # ------------------------- Geocoding ------------------------------
    if module_geocoding:
        os.chdir(os.path.join(map_kurator_system_dir ,'m_sanborn'))

        if metadata_tsv_path is not None:
            map_df = pd.read_csv(metadata_tsv_path, sep='\t')

        if not os.path.isdir(geocoding_output_dir):
            os.makedirs(geocoding_output_dir)

        for file_path in file_list:
            map_name = os.path.basename(file_path).split('.')[0]
            if metadata_tsv_path is not None:
                suffix = map_df[map_df['filename'] == map_name]['City'].values[0] # LoC sanborn
                suffix = ', ' + suffix
            else:
                suffix = ', Los Angeles' # LA sanborn

            run_geocoding_command = 'python3 s1_geocoding.py --input_map_geojson_path='+ os.path.join(stitch_output_dir,map_name + '.geojson')  + ' --output_folder=' + geocoding_output_dir + \
                ' --api_key=' + api_key + ' --user_name=' + user_name + ' --max_results=5 --geocoder_option=' + geocoder_option + ' --suffix="' + suffix + '"'
            
            time_usage = execute_command(run_geocoding_command, if_print_command)

            # break

        logging.info('Done geocoding for %s', map_name)

    
    time_geocoding = time.time()


    if module_clustering:
        os.chdir(os.path.join(map_kurator_system_dir ,'m_sanborn'))

        if not os.path.isdir(clustering_output_dir):
            os.makedirs(clustering_output_dir)

        # for file_path in file_list:
        #     map_name = os.path.basename(file_path).split('.')[0]
            
        # run_clustering_command = 'python3 s2_clustering.py --dataset_name='+ expt_name + ' --output_folder=' + geocoding_output_dir + \
        #         ' --api_key=' + api_key + ' --user_name=' + user_name + ' --max_results=5 --geocoder_option=' + geocoder_option + ' --suffix="' + suffix + '"'
        
        # time_usage = execute_command(run_clustering_command, if_print_command)


        # logging.info('Done geocoding for %s', map_name)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--map_kurator_system_dir', type=str, default='/home/zekun/dr_maps/mapkurator-system/')
    parser.add_argument('--text_spotting_model_dir', type=str, default='/home/zekun/antique_names/model/AdelaiDet/')
    
    parser.add_argument('--input_map_dir', type=str, default='/data2/mrm_sanborn_maps/LA_sanborn')
    parser.add_argument('--output_folder', type=str, default='/data2/rumsey_output')
    parser.add_argument('--expt_name', type=str, default='1000_maps') # output prefix 

    parser.add_argument('--module_get_dimension', default=False, action='store_true')
    # parser.add_argument('--module_gen_geotiff', default=False, action='store_true') # only supports dr maps
    parser.add_argument('--module_cropping', default=False, action='store_true')
    parser.add_argument('--module_text_spotting', default=False, action='store_true')
    parser.add_argument('--module_img_geojson', default=False, action='store_true')
    parser.add_argument('--module_geocoding', default=False, action='store_true') # only supports sanborn
    # parser.add_argument('--module_geocoord_geojson', default=False, action='store_true') # only supports dr maps
    # parser.add_argument('--module_entity_linking', default=False, action='store_true') # only supports dr maps
    parser.add_argument('--module_clustering', default=False, action='store_true') # only supports dr maps

    parser.add_argument('--print_command', default=False, action='store_true')

    parser.add_argument('--spotter_option', type=str, default='testr', 
        choices=['abcnet', 'testr'], 
        help='Select text spotting model option from ["abcnet","testr"]') # select text spotting model

    parser.add_argument('--geocoder_option', type=str, default='arcgis', 
        choices=['arcgis', 'google','geonames','osm'], 
        help='Select text spotting model option from ["arcgis","google","geonames","osm"]') # select text spotting model

    # params for geocoder:
    parser.add_argument('--api_key', type=str, default=None, help='api_key for geocoder. can be None if not running geocoding module')
    parser.add_argument('--user_name', type=str, default=None, help='user_name for geocoder. can be None if not running geocoding module')
    parser.add_argument('--metadata_tsv_path', type=str, default=None) # '/home/zekun/Sanborn/Sheet_List.tsv'


    args = parser.parse_args()
    print('\n')
    print(args)
    print('\n')

    run_pipeline(args)


if __name__ == '__main__':

    main()

    
