import os
import glob
import argparse
import time
import logging
import pandas as pd
from utils import get_img_path_from_external_id

logging.basicConfig(level=logging.INFO)

def run_pipeline(args):
    map_kurator_system_dir = args.map_kurator_system_dir
    text_spotting_model_dir = args.text_spotting_model_dir
    sample_map_path = args.sample_map_csv_path
    expt_prefix = args.expt_prefix
    output_folder = args.output_folder

    module_gen_geotiff = args.module_gen_geotiff
    module_text_spotting = args.module_text_spotting
    module_img_geojson = args.module_img_geojson 
    module_geocoord_geojson = args.module_geocoord_geojson 
    module_entity_linking = args.module_entity_linking

    #input_csv_path = os.path.join(map_kurator_system_dir ,sample_map_path)
    input_csv_path = sample_map_path
    sample_map_df = pd.read_csv(sample_map_path, dtype={'external_id':str})


    # geotiff_output_dir = os.path.join(map_kurator_system_dir ,'m1_geotiff/data/geotiff')
    # cropping_output_dir = os.path.join(map_kurator_system_dir, 'm2_detection_recognition', 'data/'+expt_prefix+'_crop/')
    # spotting_output_dir = os.path.join(map_kurator_system_dir, 'm2_detection_recognition', 'data/'+expt_prefix+'_crop_outabc/')
    # stitch_output_dir = os.path.join(map_kurator_system_dir, 'm2_detection_recognition', 'data/'+expt_prefix+'_geojson_abc/')
    # geojson_output_dir = os.path.join(map_kurator_system_dir, 'm4_geocoordinate_converter', 'data/'+expt_prefix+'_geojson_abc_geocoord/')

    geotiff_output_dir = os.path.join(output_folder, expt_prefix + '_geotiff')
    cropping_output_dir = os.path.join(output_folder, expt_prefix + '_crop/')
    spotting_output_dir = os.path.join(output_folder, expt_prefix + '_crop_outabc/')
    stitch_output_dir = os.path.join(output_folder, expt_prefix + '_geojson_abc/')
    geojson_output_dir = os.path.join(output_folder, expt_prefix + '_geojson_abc_geocoord/')

    external_id_to_img_path_dict = get_img_path_from_external_id( sample_map_path = input_csv_path)
    
    time_start =  time.time()
    if module_gen_geotiff:
        # run module1 to generate geotiff
        os.chdir(os.path.join(map_kurator_system_dir ,'m1_geotiff'))
        
        if not os.path.isdir(geotiff_output_dir):
            os.makedirs(geotiff_output_dir)

        run_geotiff_command = 'python convert_image_to_geotiff.py --sample_map_path '+ input_csv_path +' --out_geotiff_dir '+geotiff_output_dir  # can change params in argparse
        print(run_geotiff_command)
        os.system(run_geotiff_command)

    time_geotiff = time.time()
    logging.info('Time for generating geotiff: %d', time_geotiff - time_start)

    
    if module_text_spotting:
        
        #geotiff_path_list = glob.glob(os.path.join(geotiff_output_dir, '*.geotiff'))
        #assert(len(geotiff_path_list) != 0)

        for index, record in sample_map_df.iterrows():
            external_id = record.external_id
            img_path = external_id_to_img_path_dict[external_id]
            map_name = os.path.basename(img_path).split('.')[0]

            if img_path[-4:] == '.sid':
                continue
        
            # for geotiff_path in geotiff_path_list:
            #     #run module2: image cropping
            #     os.chdir(os.path.join(map_kurator_system_dir ,'m2_detection_recognition'))
            #     map_name = os.path.basename(geotiff_path).split('.')[0]
        
            os.chdir(os.path.join(map_kurator_system_dir ,'m2_detection_recognition'))
            if not os.path.isdir(cropping_output_dir):
                os.makedirs(cropping_output_dir)
            run_crop_command = 'python crop_img.py --img_path '+img_path + ' --output_dir '+ cropping_output_dir

            print(run_crop_command)
            os.system(run_crop_command)
        
            # run module2: text spotting
            os.chdir(text_spotting_model_dir)
            # map_name = os.path.basename(geotiff_path).split('.')[0]
        
            map_spotting_output_dir = os.path.join(spotting_output_dir,map_name)
            if not os.path.isdir(map_spotting_output_dir):
                os.makedirs(map_spotting_output_dir)
        
            run_spotting_command = 'python demo/demo.py 	--config-file configs/BAText/CTW1500/attn_R_50.yaml 	--input='+ os.path.join(cropping_output_dir,map_name) + '  --output='+ map_spotting_output_dir + '   --opts MODEL.WEIGHTS ctw1500_attn_R_50.pth'
            run_spotting_command  += ' 1> /dev/null'
            print(run_spotting_command)
            os.system(run_spotting_command)
            logging.info('Done text spotting for %s', map_name)

    time_text_spotting = time.time()
    logging.info('Time for text spotting : %d',time_text_spotting - time_geotiff)

    if module_img_geojson:
        # run module2: geojson stitching
        os.chdir(os.path.join(map_kurator_system_dir ,'m2_detection_recognition'))
        stitch_input_dir = spotting_output_dir
        
        if not os.path.isdir(stitch_output_dir):
            os.makedirs(stitch_output_dir)
        run_stitch_command = 'python stitch_output.py --input_dir '+stitch_input_dir + ' --output_dir ' + stitch_output_dir
        print(run_stitch_command)
        os.system(run_stitch_command)

    time_img_geojson = time.time()
    logging.info('Time for generating geojson in img coordinate : %d',time_img_geojson - time_text_spotting)

    if module_geocoord_geojson:
        # run module4: convert image coordinates to geocoordinates
        os.chdir(os.path.join(map_kurator_system_dir, 'm4_geocoordinate_converter'))
        
        if not os.path.isdir(geojson_output_dir):
            os.makedirs(geojson_output_dir)
        
        run_converter_command = 'python convert_geojson_to_geocoord.py --sample_map_path '+ input_csv_path +' --in_geojson_dir '+stitch_output_dir +' --out_geojson_dir '+geojson_output_dir
        print(run_converter_command)
        os.system(run_converter_command)

    time_geocoord_geojson = time.time()
    logging.info('Time for generating geojson in geo coordinate : %d',time_geocoord_geojson - time_img_geojson)

    if module_entity_linking:
        # run module5: link entities in OSM
        os.chdir(os.path.join(map_kurator_system_dir, 'm5_entity_linker'))
        geojson_linked_output_dir = os.path.join(map_kurator_system_dir, 'm5_entity_linker', 'data/100_maps_geojson_abc_linked/')
        if not os.path.isdir(geojson_output_dir):
            os.makedirs(geojson_output_dir)

        run_linker_command = 'python entity_linker.py --sample_map_path '+ input_csv_path +' --in_geojson_dir '+ geojson_output_dir +' --out_geojson_dir '+ geojson_linked_output_dir
        print(run_linker_command)
        os.system(run_linker_command)

    time_entity_linking = time.time()
    logging.info('Time for entity linking : %d',time_entity_linking - time_geocoord_geojson)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--map_kurator_system_dir', type=str, default='/home/zekun/dr_maps/mapkurator-system/')
    parser.add_argument('--text_spotting_model_dir', type=str, default='/home/zekun/antique_names/model/AdelaiDet/')
    parser.add_argument('--sample_map_csv_path', type=str, default='m1_geotiff/data/sample_US_jp2_100_maps.csv')
    parser.add_argument('--output_folder', type=str, default='/data2/dr_output')
    parser.add_argument('--expt_prefix', type=str, default='1000_maps')
    
    parser.add_argument('--module_gen_geotiff', default=False, action='store_true')
    parser.add_argument('--module_text_spotting', default=False, action='store_true')
    parser.add_argument('--module_img_geojson', default=False, action='store_true')
    parser.add_argument('--module_geocoord_geojson', default=False, action='store_true')
    parser.add_argument('--module_entity_linking', default=False, action='store_true')

                        
    args = parser.parse_args()
    print('\n')
    print(args)
    print('\n')

    run_pipeline(args)



if __name__ == '__main__':

    main()

    
