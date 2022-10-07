#!/bin/bash

python3 run_img.py --sample_map_csv_path='/data2/rumsey_output/sample_sb/data/' --expt_name='sample_sb_opt' --module_get_dimension --module_cropping

python run_img.py --sample_map_csv_path /data2/rumsey_output/sample_sb/data/ --expt_name sample_sb_opt --module_text_spotting --spotter_model testr --spotter_config /home/maplord/rumsey/TESTR/configs/TESTR/SynMap/SynMap_Polygon.yaml --output_folder /data2/rumsey_output/ --spotter_expt_name testr_syn

python3 run_img.py --sample_map_csv_path='/data2/rumsey_output/sample_sb/data/' --expt_name='sample_sb_opt' --module_img_geojson

python3 run_img.py --sample_map_csv_path='/data2/rumsey_output/sample_sb/data/' --expt_name='sample_sb_opt' --module_geocoord_geojson

python3 run_img.py --sample_map_csv_path='/data2/rumsey_output/sample_sb/data/' --expt_name='sample_sb_opt' --module_post_ocr
