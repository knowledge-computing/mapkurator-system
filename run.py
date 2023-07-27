import os
import glob
import argparse
import time
import logging
import pandas as pd
import datetime
from PIL import Image 
from utils import get_img_path_from_external_id, get_img_path_from_external_id_and_image_no,run_pipeline

import subprocess


logging.basicConfig(level=logging.INFO)
Image.MAX_IMAGE_PIXELS=None # allow reading huge images

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--map_kurator_system_dir', type=str, default='/home/maplord/rumsey/mapkurator-system/')
    parser.add_argument('--text_spotting_model_dir', type=str, default='/home/maplord/rumsey/TESTR/')
    
    parser.add_argument('--sample_map_csv_path', type=str, default=None)

    parser.add_argument('--output_folder', type=str, default='/data2/rumsey_output') # Original: /data2/rumsey_output
    parser.add_argument('--expt_name', type=str, default='1000_maps') # output prefix 
    
    parser.add_argument('--module_get_dimension', default=False, action='store_true')
    parser.add_argument('--module_gen_geotiff', default=False, action='store_true')
    parser.add_argument('--module_cropping', default=False, action='store_true')
    parser.add_argument('--module_text_spotting', default=False, action='store_true')
    parser.add_argument('--module_img_geojson', default=False, action='store_true')
    parser.add_argument('--module_geocoord_geojson', default=False, action='store_true')
    parser.add_argument('--module_post_ocr_entity_linking', default=False, action='store_true')
    parser.add_argument('--module_post_ocr_only', default=False, action='store_true')
    parser.add_argument('--module_post_ocr', default=False, action='store_true')

    parser.add_argument('--spotter_model', type=str, default='spotter-v2', choices=['testr', 'spotter-v2', "palette"], 
        help='Select text spotting model option from ["testr", "spotter-v2", "palette"]') # select text spotting model
    parser.add_argument('--spotter_config', type=str, default='/home/maplord/rumsey/TESTR/configs/TESTR/SynMap/SynMap_Polygon.yaml',
        help='Path to the config file for text spotting model')
    parser.add_argument('--spotter_expt_name', type=str, default='exp',
        help='Name of spotter experiment, if empty using config file name') 
    
    # Running spotter-testr
    # python run.py --text_spotting_model_dir /home/maplord/rumsey/spotter-testr/TESTR/
    #               --sample_map_csv_path /home/maplord/maplist_csv/luna_omo_splits/luna_omo_metadata_56628_20220724_part1.csv
    #               --expt_name 57k_maps_r3 --module_text_spotting 
    #               --spotter_model testr --spotter_config /home/maplord/rumsey/spotter-testr/TESTR/configs/TESTR/SynthMap/SynthMap_Polygon.yaml --spotter_expt_name test
    # Running spotter-v2
    # python run.py --text_spotting_model_dir /home/maplord/rumsey/spotter-v2/PALEJUN/
    #               --sample_map_csv_path /home/maplord/maplist_csv/luna_omo_splits/luna_omo_metadata_56628_20220724_part1.csv
    #               --expt_name 57k_maps_r3 --module_text_spotting 
    #               --spotter_model spotter-v2 --spotter_config /home/maplord/rumsey/spotter-v2/PALEJUN/configs/PALEJUN/SynthMap/SynthMap_Polygon.yaml --spotter_expt_name test
    # Running spotter-palette
    # python run.py --text_spotting_model_dir /home/maplord/rumsey/spotter-palette/PALETTE/
    #               --sample_map_csv_path /home/maplord/maplist_csv/luna_omo_splits/luna_omo_metadata_56628_20220724_part1.csv
    #               --expt_name 57k_maps_r3 --module_text_spotting 
    #               --spotter_model palette --spotter_config /home/maplord/rumsey/spotter-palette/PALETTR/configs/PALETTE/Pretrain/SynthMap_Polygon.yaml --spotter_expt_name test
    
    parser.add_argument('--print_command', default=False, action='store_true')
    parser.add_argument('--gpu_id', type=int, default=0)

                        
    args = parser.parse_args()
    print('\n')
    print(args)
    print('\n')

    run_pipeline(args)



if __name__ == '__main__':

    main()

    
