import os

#os.system('python crop_img.py')

map_kurator_system_dir = '/home/zekun/dr_maps/mapkurator-system/'
text_spotting_model_dir = '/home/zekun/antique_names/model/AdelaiDet/'


model_output_dir = os.path.join(map_kurator_system_dir, 'data/100_maps_crop_outabc/8628000/')

if not os.path.isdir(model_output_dir):
    os.makedirs(model_output_dir)

os.chdir(text_spotting_model_dir)

run_model_command = 'python demo/demo.py 	--config-file configs/BAText/CTW1500/attn_R_50.yaml 	--input '+ map_kurator_system_dir+'data/100_maps_crop/8628000/  --output '+ model_output_dir + '   --opts MODEL.WEIGHTS ctw1500_attn_R_50.pth'

print(run_model_command)

# execute the command                    
os.system(run_model_command)

os.chdir(os.path.join(map_kurator_system_dir ,'m2_detection_recognition'))

