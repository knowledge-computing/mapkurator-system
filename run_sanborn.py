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
    
    
    
    geotiff_output_dir = os.path.join(output_folder, expt_name,  'geotiff')
    cropping_output_dir = os.path.join(output_folder, expt_name, 'crop/')
    spotting_output_dir = os.path.join(output_folder, expt_name,  'crop_out_' + spotter_option)
    stitch_output_dir = os.path.join(output_folder, expt_name, 'geojson_' + spotter_option)
    # geojson_output_dir = os.path.join(output_folder, expt_name, 'geojson_abc_geocoord/')
    geocoding_output_dir = os.path.join(output_folder, expt_name, 'geocoding_suffix_' + spotter_option)

    # # ------------------------ Get image dimension ------------------------------
    # if module_get_dimension:
    #     for index, record in sample_map_df.iterrows():
    #         external_id = record.external_id
    #         img_path = external_id_to_img_path_dict[external_id]
    #         map_name = os.path.basename(img_path).split('.')[0]

    #         # if img_path == '/data/rumsey-jp2/162/12041157.jp2':
    #         #     continue 

    #         width, height = get_img_dimension(img_path)
            
    #         time_usage_dict[external_id]['img_w'] = width
    #         time_usage_dict[external_id]['img_h'] = height


    # # ------------------------- Generate geotiff ------------------------------
    # time_start =  time.time()
    # if module_gen_geotiff:
    #     os.chdir(os.path.join(map_kurator_system_dir ,'m1_geotiff'))
        
    #     if not os.path.isdir(geotiff_output_dir):
    #         os.makedirs(geotiff_output_dir)

    #     run_geotiff_command = 'python convert_image_to_geotiff.py --sample_map_path '+ input_csv_path +' --out_geotiff_dir '+geotiff_output_dir  # can change params in argparse
    #     time_usage = execute_command(run_geotiff_command, if_print_command)
    #     time_usage_dict['external_id']['geotiff'] = time_usage

    # time_geotiff = time.time()
    

    # ------------------------- Image cropping  ------------------------------
    if module_cropping:
        # for index, record in sample_map_df.iterrows():
        for file_path in file_list:
            img_path = os.path.join(input_map_dir, file_path)
            print(img_path)
            # external_id = record.external_id
            # img_path = external_id_to_img_path_dict[external_id]
            
            map_name = os.path.basename(img_path).split('.')[0]
            
            # if img_path[-4:] == '.sid':
            #     # convert sid to jpg
            #     redirected_path = os.path.join(sid_to_jpg_dir, map_name + '.jpg')

            #     mrsiddecode_executable="/home/zekun/dr_maps/mapkurator-system/m1_geotiff/MrSID_DSDK-9.5.4.4709-rhel6.x86-64.gcc531/Raster_DSDK/bin/mrsiddecode"

            #     run_sid_to_jpg_command = mrsiddecode_executable + ' -quiet -i '+ img_path + ' -o '+redirected_path
            #     time_usage = execute_command(run_sid_to_jpg_command, if_print_command)
            #     time_usage_dict[external_id]['conversion'] = time_usage

            #     img_path = redirected_path
                

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

            # external_id = record.external_id
            # img_path = external_id_to_img_path_dict[external_id]
            # map_name = os.path.basename(img_path).split('.')[0]


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
            # time_usage_dict[external_id]['spotting'] = time_usage

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
        os.chdir(os.path.join(map_kurator_system_dir ,'m2_detection_recognition'))

        if metadata_tsv_path is not None:
            map_df = pd.read_csv(metadata_tsv_path, sep='\t')

        if not os.path.isdir(geocoding_output_dir):
            os.makedirs(geocoding_output_dir)

        for file_path in file_list:
            map_name = os.path.basename(file_path).split('.')[0]

            if metadata_tsv_path is not None:
                suffix = map_df[map_df['filename'] == map_name]['City'].values[0] # LoC sanborn
            else:
                suffix = ', Los Angeles' # LA sanborn

            run_geocoding_command = 'python3 geocoding.py --input_map_geojson_path='+ os.path.join(stitch_output_dir,map_name + '.geojson')  + ' --output_folder=' + geocoding_output_dir + \
                ' --api_key=' + api_key + ' --user_name=' + user_name + ' --max_results=5 --geocoder_option=' + geocoder_option + ' --suffix=' + suffix
            
            time_usage = execute_command(run_geocoding_command, if_print_command)

            # break


        logging.info('Done geocoding for %s', map_name)

    
    time_geocoding = time.time()
    

    # # ------------------------- Convert image coordinates to geocoordinates ------------------------------
    # if module_geocoord_geojson:
    #     os.chdir(os.path.join(map_kurator_system_dir, 'm4_geocoordinate_converter'))
        
    #     if not os.path.isdir(geojson_output_dir):
    #         os.makedirs(geojson_output_dir)
        
    #     run_converter_command = 'python convert_geojson_to_geocoord.py --sample_map_path '+ input_csv_path +' --in_geojson_dir '+stitch_output_dir +' --out_geojson_dir '+geojson_output_dir
    #     execute_command(run_converter_command, if_print_command)

    # time_geocoord_geojson = time.time()

    

    # # ------------------------- Link entities in OSM ------------------------------
    # # To jina: 
    # # remember to change output dir (according to Line69-73)
    # # time usage logging for each map - write to time_usage_df 
    # #  -zekun
    # if module_entity_linking:
    #     os.chdir(os.path.join(map_kurator_system_dir, 'm5_entity_linker'))
        
    #     geojson_linked_output_dir = os.path.join(map_kurator_system_dir, 'm5_entity_linker', 'data/100_maps_geojson_abc_linked/')
    #     if not os.path.isdir(geojson_output_dir):
    #         os.makedirs(geojson_output_dir)

    #     run_linker_command = 'python entity_linker.py --sample_map_path '+ input_csv_path +' --in_geojson_dir '+ geojson_output_dir +' --out_geojson_dir '+ geojson_linked_output_dir
    #     execute_command(run_linker_command, if_print_command)

    # time_entity_linking = time.time()
    
    # # --------------------- Time usage logging --------------------------
    # print('\n')
    # logging.info('Time for generating geotiff: %d', time_geotiff - time_start)
    # logging.info('Time for Cropping : %d',time_cropping - time_geotiff)
    # logging.info('Time for text spotting : %d',time_text_spotting - time_cropping)
    # logging.info('Time for generating geojson in img coordinate : %d',time_img_geojson - time_text_spotting)
    # logging.info('Time for generating geojson in geo coordinate : %d',time_geocoord_geojson - time_img_geojson)
    # logging.info('Time for entity linking : %d',time_entity_linking - time_geocoord_geojson)

    # time_usage_df = pd.DataFrame.from_dict(time_usage_dict, orient='index')
    # time_usage_log_path = os.path.join(output_folder, expt_name, 'time_usage.csv')

    
    # # check if exist time_usage log file 
    # if os.path.isfile(time_usage_log_path):
    #     existing_df = pd.read_csv(time_usage_log_path, index_col='external_id', dtype={'external_id':str})
    #     # if exist duplicate columns, ret time usage values to the latest run
    #     cols_to_use = existing_df.columns.difference(time_usage_df.columns)

    #     time_usage_df = time_usage_df.join(existing_df[cols_to_use])

    #     # make sure time_usage_expt_name.csv always have the latest time usage
    #     m_time = os.path.getmtime(time_usage_log_path)
    #     dt_m = datetime.datetime.fromtimestamp(m_time)
    #     timestr = dt_m.strftime("%Y%m%d-%H%M%S") 
    #     deprecated_path = os.path.join(output_folder, expt_name, 'time_usage_' +  timestr +'.csv')
    #     run_command = 'mv ' + time_usage_log_path + ' ' + deprecated_path
    #     execute_command(run_command, if_print_command)

    # time_usage_df.to_csv(time_usage_log_path, index_label='external_id')

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--map_kurator_system_dir', type=str, default='/home/zekun/dr_maps/mapkurator-system/')
    parser.add_argument('--text_spotting_model_dir', type=str, default='/home/zekun/antique_names/model/AdelaiDet/')
    
    parser.add_argument('--input_map_dir', type=str, default='/data2/sanborn_maps/LA_sanborn')
    parser.add_argument('--output_folder', type=str, default='/data2/rumsey_output')
    parser.add_argument('--expt_name', type=str, default='1000_maps') # output prefix 

    
    parser.add_argument('--module_get_dimension', default=False, action='store_true')
    parser.add_argument('--module_gen_geotiff', default=False, action='store_true') # only supports dr maps
    parser.add_argument('--module_cropping', default=False, action='store_true')
    parser.add_argument('--module_text_spotting', default=False, action='store_true')
    parser.add_argument('--module_img_geojson', default=False, action='store_true')
    parser.add_argument('--module_geocoding', default=False, action='store_true') # only supports sanborn
    parser.add_argument('--module_geocoord_geojson', default=False, action='store_true') # only supports dr maps
    parser.add_argument('--module_entity_linking', default=False, action='store_true') # only supports dr maps

    parser.add_argument('--print_command', default=False, action='store_true')

    parser.add_argument('--spotter_option', type=str, default='testr', 
        choices=['abcnet', 'testr'], 
        help='Select text spotting model option from ["abcnet","testr"]') # select text spotting model

    parser.add_argument('--geocoder_option', type=str, default='arcgis', 
        choices=['arcgis', 'google','geonames'], 
        help='Select text spotting model option from ["arcgis","google","geonames"]') # select text spotting model

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

    
