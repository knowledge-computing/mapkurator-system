import os
import glob

map_kurator_system_dir = '/home/zekun/dr_maps/mapkurator-system/'
text_spotting_model_dir = '/home/zekun/antique_names/model/AdelaiDet/'


# run module1 to generate geotiff
os.chdir(os.path.join(map_kurator_system_dir ,'m1_geotiff'))
geotiff_output_dir = os.path.join(map_kurator_system_dir ,'m1_geotiff/data/geotiff')
if not os.path.isdir(geotiff_output_dir):
    os.makedirs(geotiff_output_dir)

run_geotiff_command = 'python convert_image_to_geotiff.py --out_geotif_dir '+geotiff_output_dir  # can change params in argparse
#os.system(run_geotiff_command)


# run module2: image cropping
os.chdir(os.path.join(map_kurator_system_dir ,'m2_detection_recognition'))
geotiff_path_list = glob.glob(os.path.join(geotiff_output_dir, '*.geotiff'))

for geotiff_path in geotiff_path_list:
    map_name = os.path.basename(geotiff_path).split('.')[0]

    cropping_output_dir = os.path.join(map_kurator_system_dir, 'm2_detection_recognition', 'data/100_maps_crop/',map_name)
    if not os.path.isdir(cropping_output_dir):
        os.makedirs(cropping_output_dir)
    run_crop_command = 'python crop_img.py --img_path '+geotiff_path + ' --output_dir '+ cropping_output_dir
    print(run_crop_command)
    os.system(run_crop_command)

# run module2: text spotting
os.chdir(text_spotting_model_dir)
for geotiff_path in geotiff_path_list:
    map_name = os.path.basename(geotiff_path).split('.')[0]

    spotting_output_dir = os.path.join(map_kurator_system_dir, 'm2_detection_recognition', 'data/100_maps_crop_outabc/',map_name)
    if not os.path.isdir(spotting_output_dir):
        os.makedirs(spotting_output_dir)

    run_spotting_command = 'python demo/demo.py 	--config-file configs/BAText/CTW1500/attn_R_50.yaml 	--input '+ map_kurator_system_dir+'/m2_detection_recognition/data/100_maps_crop/'+map_name+'  --output '+ spotting_output_dir + '   --opts MODEL.WEIGHTS ctw1500_attn_R_50.pth'
    print(run_spotting_command)               
    os.system(run_spotting_command)


# run module2: geojson stitching
os.chdir(os.path.join(map_kurator_system_dir ,'m2_detection_recognition'))

for geotiff_path in geotiff_path_list:
    map_name = os.path.basename(geotiff_path).split('.')[0]
    spotting_output_dir = os.path.join(map_kurator_system_dir, 'm2_detection_recognition', 'data/100_maps_crop_outabc/',map_name)
    stitch_output_dir = os.path.join(map_kurator_system_dir, 'm2_detection_recognition', 'data/100_maps_geojson_abc/')
    if not os.path.isdir(stitch_output_path):
        os.makedirs(stitch_output_path)
    run_stitch_command = 'python stitch_output.py --input_dir '+spotting_output_dir + ' --output_dir ' + stitch_output_dir 
    #run_crop_command = 'python crop_img.py --img_path '+geotiff_path + ' --output_dir '+ cropping_output_dir
    print(run_stitch_command)