#!/bin/bash

python3 run.py --sample_map_csv_path='/home/maplord/maplist_csv/luna_omo_metadata_2508.csv' --expt_name='Rerun_2_2508' --module_get_dimension --module_cropping

python run.py --sample_map_csv_path //home/maplord/maplist_csv/luna_omo_metadata_2508.csv --expt_name Rerun_2_2508 --module_text_spotting --spotter_model testr --spotter_config /home/maplord/rumsey/TESTR/configs/TESTR/SynMap/SynMap_Polygon.yaml --output_folder /data2/rumsey_output/ --spotter_expt_name testr_syn

python3 run.py --sample_map_csv_path='/home/maplord/maplist_csv/luna_omo_metadata_2508.csv' --expt_name='Rerun_2_2508' --module_img_geojson

python3 run.py --sample_map_csv_path='/home/maplord/maplist_csv/luna_omo_metadata_2508.csv' --expt_name='Rerun_2_2508' --module_geocoord_geojson

python3 run.py --sample_map_csv_path='/home/maplord/maplist_csv/luna_omo_metadata_2508.csv' --expt_name='Rerun_2_2508' --module_post_ocr
