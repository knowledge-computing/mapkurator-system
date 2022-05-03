import os
import glob

# map_kurator_system_dir = '/home/zekun/dr_maps/mapkurator-system/'
map_kurator_system_dir = '/Users/jinak/mapkurator-system/'
# text_spotting_model_dir = '/home/zekun/antique_names/model/AdelaiDet/'
sample_map_path = 'm1_geotiff/data/sample_US_jp2_100_maps.csv'

# # run module1 to generate geotiff
# os.chdir(os.path.join(map_kurator_system_dir ,'m1_geotiff'))
# input_csv = os.path.join(map_kurator_system_dir ,sample_map_path)
# geotiff_output_dir = os.path.join(map_kurator_system_dir ,'m1_geotiff/data/geotiff')
# if not os.path.isdir(geotiff_output_dir):
#     os.makedirs(geotiff_output_dir)

# run_geotiff_command = 'python convert_image_to_geotiff.py --sample_map_path '+ input_csv +' --out_geotiff_dir '+geotiff_output_dir  # can change params in argparse
# print(run_geotiff_command)
# #os.system(run_geotiff_command)


# # run module2: image cropping

# geotiff_path_list = glob.glob(os.path.join(geotiff_output_dir, '*.geotiff'))
# assert(len(geotiff_path_list) != 0)

# for geotiff_path in geotiff_path_list:
#     os.chdir(os.path.join(map_kurator_system_dir ,'m2_detection_recognition'))
#     map_name = os.path.basename(geotiff_path).split('.')[0]

#     cropping_output_dir = os.path.join(map_kurator_system_dir, 'm2_detection_recognition', 'data/100_maps_crop/')
#     if not os.path.isdir(cropping_output_dir):
#         os.makedirs(cropping_output_dir)
#     run_crop_command = 'python crop_img.py --img_path '+geotiff_path + ' --output_dir '+ cropping_output_dir
#     print(run_crop_command)
#     os.system(run_crop_command)

#     # run module2: text spotting
#     os.chdir(text_spotting_model_dir)
#     map_name = os.path.basename(geotiff_path).split('.')[0]

#     spotting_output_dir = os.path.join(map_kurator_system_dir, 'm2_detection_recognition', 'data/100_maps_crop_outabc/',map_name)
#     if not os.path.isdir(spotting_output_dir):
#         os.makedirs(spotting_output_dir)

#     run_spotting_command = 'python demo/demo.py 	--config-file configs/BAText/CTW1500/attn_R_50.yaml 	--input '+ map_kurator_system_dir+'/m2_detection_recognition/data/100_maps_crop/'+map_name+'  --output '+ spotting_output_dir + '   --opts MODEL.WEIGHTS ctw1500_attn_R_50.pth'
#     run_spotting_command  += ' 1> /dev/null'
#     print(run_spotting_command)               
#     os.system(run_spotting_command)

#     #break


# run module2: geojson stitching
# os.chdir(os.path.join(map_kurator_system_dir ,'m2_detection_recognition'))
#
#
# stitch_input_dir = os.path.join(map_kurator_system_dir, 'm2_detection_recognition', 'data/100_maps_crop_outabc/')
stitch_output_dir = os.path.join(map_kurator_system_dir, 'm2_detection_recognition', 'data/100_maps_geojson_abc/')
# if not os.path.isdir(stitch_output_dir):
#     os.makedirs(stitch_output_dir)
# run_stitch_command = 'python stitch_output.py --input_dir '+stitch_input_dir + ' --output_dir ' + stitch_output_dir
# print(run_stitch_command)
# os.system(run_stitch_command)



# run module4: convert image coordinates to geocoordinates
os.chdir(os.path.join(map_kurator_system_dir, 'm4_geocoordinate_converter'))
input_csv = os.path.join(map_kurator_system_dir, sample_map_path)
geojson_output_dir = os.path.join(map_kurator_system_dir, 'm4_geocoordinate_converter', 'data/100_maps_geojson_abc_geocoord/')
if not os.path.isdir(geojson_output_dir):
    os.makedirs(geojson_output_dir)

run_converter_command = 'python convert_geojson_to_geocoord.py --sample_map_path '+ input_csv +' --in_geojson_dir '+stitch_output_dir +' --out_geojson_dir '+geojson_output_dir
print(run_converter_command)
os.system(run_converter_command)