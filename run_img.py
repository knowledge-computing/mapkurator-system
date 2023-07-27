import os
import subprocess
import glob
import argparse
import time
import logging
import pandas as pd
import pdb
import datetime
from PIL import Image 
from utils import run_pipeline

import subprocess

#this code is the case for getting an input as folders which include images.  
#tested image : /home/maplord/rumsey/mapkurator-system/data/100_maps_crop/crop_leeje_2/test_run_img/
logging.basicConfig(level=logging.INFO)
Image.MAX_IMAGE_PIXELS=None # allow reading huge images



def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--map_kurator_system_dir', type=str, default='/home/maplord/rumsey/mapkurator-system/')
    parser.add_argument('--text_spotting_model_dir', type=str, default='/home/maplord/rumsey/TESTR/')

    parser.add_argument('--input_dir_path', type=str, default=None)

    parser.add_argument('--output_folder', type=str, default='/data2/rumsey_output') 
    parser.add_argument('--expt_name', type=str, default='1000_maps') # output prefix 
    
    parser.add_argument('--module_get_dimension', default=False, action='store_true')
    parser.add_argument('--module_gen_geotiff', default=False, action='store_true')
    parser.add_argument('--module_cropping', default=False, action='store_true')
    parser.add_argument('--module_text_spotting', default=False, action='store_true')
    parser.add_argument('--module_img_geojson', default=False, action='store_true')

    
    parser.add_argument('--spotter_model', type=str, default='spotter-v2', choices=['testr', 'spotter-v2', "palette"], 
        help='Select text spotting model option from ["testr", "spotter-v2", "palette"]') # select text spotting model
    parser.add_argument('--spotter_config', type=str, default='/home/maplord/rumsey/TESTR/configs/TESTR/SynMap/SynMap_Polygon.yaml',
        help='Path to the config file for text spotting model')
    parser.add_argument('--spotter_expt_name', type=str, default='exp',
        help='Name of spotter experiment, if empty using config file name') 
   
    parser.add_argument('--print_command', default=False, action='store_true')
    parser.add_argument('--gpu_id', type=int, default=0)
                        
    args = parser.parse_args()
    print('\n')
    print(args)
    print('\n')

    run_pipeline(args)



if __name__ == '__main__':

    main()

    
