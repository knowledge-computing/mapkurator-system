import os
import glob
import pandas as pd
import ast
import argparse
import logging
import pdb
from PIL import Image 
import datetime
import subprocess
import time

logging.basicConfig(level=logging.INFO)
Image.MAX_IMAGE_PIXELS=None 


def execute_command(command, if_print_command):
    t1 = time.time()

    if if_print_command:
        print(command)

    try:
        subprocess.run(command, shell=True,check=True, capture_output = True) #stderr=subprocess.STDOUT)
        t2 = time.time()
        time_usage = t2 - t1 
        return {'time_usage':time_usage}
    except subprocess.CalledProcessError as err:
        error = err.stderr.decode('utf8')
        # format error message to one line
        error  = error.replace('\n','\t')
        error = error.replace(',',';')
        return {'error': error}


def get_img_dimension(img_path):
    map_img = Image.open(img_path) 
    width, height = map_img.size 

    return width, height


def run_pipeline(args):
    # -------------------------  Pass arguments -----------------------------------------
    map_kurator_system_dir = args.map_kurator_system_dir
    text_spotting_model_dir = args.text_spotting_model_dir

    if hasattr(args, "sample_map_csv_path"):
    # if  typeof === 'undefined':  
        sample_map_path = args.sample_map_csv_path
        module_geocoord_geojson = args.module_geocoord_geojson 
        module_post_ocr_entity_linking = args.module_post_ocr_entity_linking
        module_post_ocr_only = args.module_post_ocr_only
        module_post_ocr = args.module_post_ocr
    
    elif hasattr(args, "input_dir_path"): 
        input_dir_path = args.input_dir_path

    expt_name = args.expt_name
    output_folder = args.output_folder

    module_get_dimension = args.module_get_dimension
    module_gen_geotiff = args.module_gen_geotiff
    module_cropping = args.module_cropping
    module_text_spotting = args.module_text_spotting
    module_img_geojson = args.module_img_geojson 

    spotter_model = args.spotter_model
    spotter_config = args.spotter_config
    spotter_expt_name = args.spotter_expt_name
    gpu_id = args.gpu_id
    
    if_print_command = args.print_command
    error_reason_dict = dict()

    if "sample_map_path" in locals():
        # ------------------------- Read sample map list and prepare output dir ----------------
        if sample_map_path is not None:
            input_csv_path = sample_map_path
            if input_csv_path[-4:] == '.csv':
                sample_map_df = pd.read_csv(sample_map_path, dtype={'external_id':str})
            elif input_csv_path[-4:] == '.tsv':
                sample_map_df = pd.read_csv(sample_map_path, dtype={'external_id':str}, sep='\t')
            else:
                raise NotImplementedError

        external_id_to_img_path_dict, unmatched_external_id_list = get_img_path_from_external_id_and_image_no( sample_map_path = input_csv_path)

        # initialize error reason dict
        
        for ex_id in unmatched_external_id_list:
            error_reason_dict[ex_id] = {'img_path':None, 'error':'Can not find image given external_id.'} 
    
    elif "input_dir_path" in locals():
        if input_dir_path is not None: 
            input_img_path = input_dir_path 
            sample_map_df = pd.DataFrame(columns = ["external_id"])
            for images in os.listdir(input_img_path):
                    tmp_path={"external_id": os.path.join(input_img_path,images)}
                    sample_map_df=sample_map_df.append(tmp_path,ignore_index=True)
        else:
            raise NotImplementedError            
    else:
        raise NotImplementedError


    expt_out_dir = os.path.join(output_folder, expt_name)
    geotiff_output_dir = os.path.join(output_folder, expt_name,  'geotiff')
    cropping_output_dir = os.path.join(output_folder, expt_name, 'crop/')
    spotting_output_dir = os.path.join(output_folder, expt_name,  'spotter/' + spotter_expt_name)
    stitch_output_dir = os.path.join(output_folder, expt_name, 'stitch/' + spotter_expt_name)
    geocoord_output_dir = os.path.join(output_folder, expt_name, 'geocoord/' + spotter_expt_name)
    postocr_linking_output_dir = os.path.join(output_folder, expt_name, 'postocr_linking/'+ spotter_expt_name)
    postocr_only_output_dir = os.path.join(output_folder, expt_name, 'postocr_only/'+ spotter_expt_name)


    if not os.path.isdir(expt_out_dir):
        os.makedirs(expt_out_dir)

    # ------------------------ Get image dimension  ------------------------------
    if module_get_dimension:
        for index, record in sample_map_df.iterrows():
            external_id = record.external_id
            # pdb.set_trace()
            if "sample_map_path" in locals():
                if external_id not in external_id_to_img_path_dict:
                    error_reason_dict[external_id] = {'img_path':None, 'error':'key not in external_id_to_img_path_dict'} 
                    continue 

                img_path = external_id_to_img_path_dict[external_id]

                try:
                    width, height = get_img_dimension(img_path)
                except Exception as e:
                    error_reason_dict[external_id] = {'img_path':img_path, 'error': e } 

            elif "input_dir_path" in locals():
                img_path = sample_map_df['external_id'].iloc[index]              
                width, height = get_img_dimension(img_path)        
            
            map_name = os.path.basename(img_path).split('.')[0]
            
    # ------------------------- Generate geotiff ------------------------------
    time_start =  time.time()
    if module_gen_geotiff:
        os.chdir(os.path.join(map_kurator_system_dir ,'m1_geotiff'))
        
        if not os.path.isdir(geotiff_output_dir):
            os.makedirs(geotiff_output_dir)

        # use converted jpg folder instead of original sid folder
        if "sample_map_path" in locals():
            merged_input_path=sample_map_path
        else: 
            merged_input_path=input_dir_path

            run_geotiff_command = 'python convert_image_to_geotiff.py --sid_root_dir /data2/rumsey_sid_to_jpg/ --sample_map_path '+ merged_input_path +' --out_geotiff_dir '+geotiff_output_dir  # can change params in argparse
            exe_ret = execute_command(run_geotiff_command, if_print_command)
            if 'error' in exe_ret:
                error = exe_ret['error']

        

    # ------------------------- Image cropping  ------------------------------
    if module_cropping:
        for index, record in sample_map_df.iterrows():
            external_id = record.external_id
            if "sample_map_path" in locals():
                if external_id not in external_id_to_img_path_dict:
                    error_reason_dict[external_id] = {'img_path':None, 'error':'key not in external_id_to_img_path_dict'} 
                    continue 
                img_path = external_id_to_img_path_dict[external_id]
            else: 
                img_path = sample_map_df['external_id'].iloc[index]

            map_name = os.path.basename(img_path).split('.')[0]

            os.chdir(os.path.join(map_kurator_system_dir ,'m2_detection_recognition'))
            if not os.path.isdir(cropping_output_dir):
                os.makedirs(cropping_output_dir)
            
            run_crop_command = 'python crop_img.py --img_path '+img_path + ' --output_dir '+ cropping_output_dir

            exe_ret = execute_command(run_crop_command, if_print_command)
            
            if "sample_map_path" in locals():
                if 'error' in exe_ret:
                    error = exe_ret['error']
                    error_reason_dict[external_id] = {'img_path':img_path, 'error': error } 

                
            
    time_cropping = time.time()
    
    # ------------------------- Text Spotting (patch level) ------------------------------
    if module_text_spotting:
        assert os.path.exists(spotter_config), "Config file for spotter must exist!"
        os.chdir(text_spotting_model_dir) 
        os.system("python setup.py build develop 1> /dev/null")

        for index, record in sample_map_df.iterrows():

            external_id = record.external_id
            if "sample_map_path" in locals():
                if external_id not in external_id_to_img_path_dict:
                    error_reason_dict[external_id] = {'img_path':None, 'error':'key not in external_id_to_img_path_dict'} 
                    continue 
                img_path = external_id_to_img_path_dict[external_id]
            else:
                img_path = sample_map_df['external_id'].iloc[index]

            map_name = os.path.basename(img_path).split('.')[0]
            # print(map_name)

            map_spotting_output_dir = os.path.join(spotting_output_dir, map_name)
            
            if not os.path.isdir(map_spotting_output_dir):
                os.makedirs(map_spotting_output_dir)
            else:
                num_existing_json = len(glob.glob(os.path.join(map_spotting_output_dir, '*.json')))
                num_existing_images = len(glob.glob(os.path.join(cropping_output_dir, map_name, '*jpg')))
                if num_existing_json == num_existing_images:
                    continue
                else:
                    print(f'{index}/{len(sample_map_df)}: Re-run spotting for map {map_name}')
                    import shutil
                    shutil.rmtree(map_spotting_output_dir)
                    os.makedirs(map_spotting_output_dir)        

            if spotter_model in ['testr', 'spotter-v2', 'palette']:
                run_spotting_command = f'CUDA_VISIBLE_DEVICES={gpu_id} python tools/inference.py --config-file {spotter_config} --output_json --input {os.path.join(cropping_output_dir,map_name)} --output {map_spotting_output_dir}'
            else:
                raise NotImplementedError
            
            # print(run_spotting_command)
            run_spotting_command  += ' 1> /dev/null'
        
            exe_ret = execute_command(run_spotting_command, if_print_command)  
            if "sample_map_path" in locals():   
                if 'error' in exe_ret:
                    error = exe_ret['error']
                    error_reason_dict[external_id] = {'img_path':img_path, 'error': error } 
            
            # elif 'time_usage' in exe_ret:
            #     time_usage = exe_ret['time_usage']
            #     time_usage_dict[external_id]['spotting'] = time_usage
            # else:
            #     raise NotImplementedError

            logging.info(f'{index}/{len(sample_map_df)}: Done text spotting for {map_name}')
            
    # time_text_spotting = time.time()
    

    # ------------------------- Image coord geojson (map level) ------------------------------
    if module_img_geojson:
        os.chdir(os.path.join(map_kurator_system_dir ,'m3_image_geojson'))
        
        if not os.path.isdir(stitch_output_dir):
            os.makedirs(stitch_output_dir)

        for index, record in sample_map_df.iterrows():
            external_id = record.external_id
            if "sample_map_path" in locals():
                if external_id not in external_id_to_img_path_dict:
                    error_reason_dict[external_id] = {'img_path':None, 'error':'key not in external_id_to_img_path_dict'} 
                    continue 
                img_path = external_id_to_img_path_dict[external_id]
            else: 
                img_path = sample_map_df['external_id'].iloc[index]
            map_name = os.path.basename(img_path).split('.')[0]

            stitch_input_dir = os.path.join(spotting_output_dir, map_name)
            output_geojson = os.path.join(stitch_output_dir, map_name + '.geojson')
            
            run_stitch_command = 'python stitch_output.py --input_dir '+stitch_input_dir + ' --output_geojson ' + output_geojson
            
            exe_ret = execute_command(run_stitch_command, if_print_command)

            if "sample_map_path" in locals():
                if 'error' in exe_ret:
                    error = exe_ret['error']
                    error_reason_dict[external_id] = {'img_path':img_path, 'error': error } 

            # elif 'time_usage' in exe_ret:
            #     time_usage = exe_ret['time_usage']
            #     time_usage_dict[external_id]['stitch'] = time_usage
            # else:
            #     raise NotImplementedError
            
    # time_img_geojson = time.time()


    # ------------------------- post-OCR ------------------------------
    if "sample_map_path" in locals():
        if module_post_ocr:
            os.chdir(os.path.join(map_kurator_system_dir, 'm4_post_ocr'))

            if not os.path.isdir(postocr_only_output_dir):
                os.makedirs(postocr_only_output_dir)
            
            for index, record in sample_map_df.iterrows():
                
                external_id = record.external_id
                if external_id not in external_id_to_img_path_dict:
                    error_reason_dict[external_id] = {'img_path': None, 'error': 'key not in external_id_to_img_path_dict'}
                    continue

                img_path = external_id_to_img_path_dict[external_id]
                map_name = os.path.basename(img_path).split('.')[0]
                
                input_geojson_file = os.path.join(geocoord_output_dir, map_name + '.geojson')

                run_postocr_command = 'python post_ocr_main.py --in_geojson_file '+ input_geojson_file + ' --out_geojson_dir ' + os.path.join(map_kurator_system_dir, postocr_only_output_dir)
                
                exe_ret = execute_command(run_postocr_command, if_print_command)
                
                if 'error' in exe_ret:
                    error = exe_ret['error']
                    error_reason_dict[external_id] = {'img_path':img_path, 'error': error }

    #         elif 'time_usage' in exe_ret:
    #             time_usage = exe_ret['time_usage']
    #             time_usage_dict[external_id]['geocoord_geojson'] = time_usage
    #         else:
    #             raise NotImplementedError

        # time_geocoord_geojson = time.time()

    # ------------------------- Convert image coordinates to geocoordinates ------------------------------
    if "sample_map_path" in locals():
        if module_geocoord_geojson:
            os.chdir(os.path.join(map_kurator_system_dir, 'm5_geocoordinate_converter'))

            if not os.path.isdir(geocoord_output_dir):
                os.makedirs(geocoord_output_dir)

            for index, record in sample_map_df.iterrows():
                external_id = record.external_id
                if external_id not in external_id_to_img_path_dict:
                    error_reason_dict[external_id] = {'img_path': None,
                                                    'error': 'key not in external_id_to_img_path_dict'}
                    continue

                img_path = external_id_to_img_path_dict[external_id]
                map_name = os.path.basename(img_path).split('.')[0]

                # current_files_list = glob.glob(os.path.join(map_kurator_system_dir, geocoord_output_dir, "*.geojson"))

                # saved_map_list = []
                # for mapname in current_files_list:
                #     only_map = mapname.split("/")[-1]#.strip().replace(".geojson", "")
                #     saved_map_list.append(only_map)
              
                in_geojson = os.path.join(stitch_output_dir, map_name + '.geojson')
                
                # current_map = in_geojson.split("/")[-1]

                # if current_map not in saved_map_list: 
                    # print("running missing file",current_map)

                run_converter_command = 'python convert_geojson_to_geocoord.py --sample_map_path ' + os.path.join(map_kurator_system_dir, input_csv_path) + ' --in_geojson_file ' + in_geojson + ' --out_geojson_dir ' + os.path.join(map_kurator_system_dir, geocoord_output_dir)

                exe_ret = execute_command(run_converter_command, if_print_command)

                if 'error' in exe_ret:
                    error = exe_ret['error']
                    error_reason_dict[external_id] = {'img_path': img_path, 'error': error}

#             elif 'time_usage' in exe_ret:
#                 time_usage = exe_ret['time_usage']
#                 time_usage_dict[external_id]['geocoord_geojson'] = time_usage
#             else:
#                 raise NotImplementedError

#     time_geocoord_geojson = time.time()


    # --------------------- Error logging --------------------------
    print('\n')
    current_time = datetime.datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
    error_reason_df = pd.DataFrame.from_dict(error_reason_dict, orient='index')
    error_reason_log_path = os.path.join(output_folder, expt_name, 'error_reason_' +  current_time +'.csv')
    error_reason_df.to_csv(error_reason_log_path, index_label='external_id')


def func_file_to_fullpath_dict(file_path_list):

    file_fullpath_dict = dict()
    for file_path in file_path_list:
        file_fullpath_dict[os.path.basename(file_path).split('.')[0]] = file_path

    return file_fullpath_dict  

def get_img_path_from_external_id(jp2_root_dir = '/data/rumsey-jp2/', sid_root_dir = '/data2/rumsey_sid_to_jpg/', additional_root_dir='/data2/rumsey-luna-img/', sample_map_path = None,external_id_key = 'external_id') :
    # returns (1) a dict with external-id as key, full image path as value (2) list of external-id that can not find image path

    jp2_file_path_list = glob.glob(os.path.join(jp2_root_dir, '*/*.jp2'))
    sid_file_path_list = glob.glob(os.path.join(sid_root_dir, '*.jpg'))
    add_file_path_list = glob.glob(os.path.join(additional_root_dir, '*'))

    jp2_file_fullpath_dict = func_file_to_fullpath_dict(jp2_file_path_list) 
    sid_file_fullpath_dict = func_file_to_fullpath_dict(sid_file_path_list) 
    add_file_fullpath_dict = func_file_to_fullpath_dict(add_file_path_list) 

    sample_map_df = pd.read_csv(sample_map_path, dtype={'external_id':str})

    external_id_to_img_path_dict = {}

    unmatched_external_id_list = []

    for index, record in sample_map_df.iterrows():
        external_id = record.external_id
        filename_without_extension = external_id.strip("'").replace('.','')

        full_path = ''
        if filename_without_extension in jp2_file_fullpath_dict:
            full_path = jp2_file_fullpath_dict[filename_without_extension]
        elif filename_without_extension in sid_file_fullpath_dict:
            full_path = sid_file_fullpath_dict[filename_without_extension]
        elif filename_without_extension in add_file_fullpath_dict:
            full_path = add_file_fullpath_dict[filename_without_extension]
        else:
            # print('image with external_id not found in image_dir:', external_id)
            unmatched_external_id_list.append(external_id)
            continue
        assert (len(full_path)!=0)

        external_id_to_img_path_dict[external_id] = full_path
    
    return external_id_to_img_path_dict,  unmatched_external_id_list

def get_img_path_from_external_id_and_image_no(jp2_root_dir = '/data/rumsey-jp2/', sid_root_dir = '/data2/rumsey_sid_to_jpg/', additional_root_dir='/data2/rumsey-luna-img/', sample_map_path = None,external_id_key = 'external_id') :
    # returns (1) a dict with external-id as key, full image path as value (2) list of external-id that can not find image path

    jp2_file_path_list = glob.glob(os.path.join(jp2_root_dir, '*/*.jp2'))
    sid_file_path_list = glob.glob(os.path.join(sid_root_dir, '*.jpg')) # use converted jpg directly
    add_file_path_list = glob.glob(os.path.join(additional_root_dir, '*'))

    jp2_file_fullpath_dict = func_file_to_fullpath_dict(jp2_file_path_list) 
    sid_file_fullpath_dict = func_file_to_fullpath_dict(sid_file_path_list) 
    add_file_fullpath_dict = func_file_to_fullpath_dict(add_file_path_list) 

    sample_map_df = pd.read_csv(sample_map_path, dtype={'external_id':str})

    external_id_to_img_path_dict = {}

    unmatched_external_id_list = []
    for index, record in sample_map_df.iterrows():
        external_id = record.external_id 
        image_no = record.image_no
        # filename_without_extension = external_id.strip("'").replace('.','')
        filename_without_extension = image_no.strip("'").split('.')[0]

        full_path = ''
        if filename_without_extension in jp2_file_fullpath_dict:
            full_path = jp2_file_fullpath_dict[filename_without_extension]
        elif filename_without_extension in sid_file_fullpath_dict:
            full_path = sid_file_fullpath_dict[filename_without_extension]
        elif filename_without_extension in add_file_fullpath_dict:
            full_path = add_file_fullpath_dict[filename_without_extension]
        else:
            print('image with external_id not found in image_dir:', external_id)
            unmatched_external_id_list.append(external_id)
            continue
        assert (len(full_path)!=0)

        external_id_to_img_path_dict[external_id] = full_path
    
    return external_id_to_img_path_dict, unmatched_external_id_list


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--jp2_root_dir', type=str, default='/data/rumsey-jp2/',
                        help='image dir of jp2 files.')
    parser.add_argument('--sid_root_dir', type=str, default='/data2/rumsey_sid_to_jpg/',
                        help='image dir of sid files.')
    parser.add_argument('--additional_root_dir', type=str, default='/data2/rumsey-luna-img/',
                        help='image dir of additional luna files.')
    parser.add_argument('--sample_map_path', type=str, default='data/initial_US_100_maps.csv',
                        help='path to sample map csv, which contains gcps info')
    parser.add_argument('--external_id_key', type=str, default='external_id',
                        help='key string for external id, could be external_id or ListNo')
 
    args = parser.parse_args()
    print(args)

    # get_img_path_from_external_id(jp2_root_dir = args.jp2_root_dir, sid_root_dir = args.sid_root_dir, additional_root_dir = args.additional_root_dir,
    # sample_map_path = args.sample_map_path,external_id_key = args.external_id_key)

    get_img_path_from_external_id_and_image_no(jp2_root_dir = args.jp2_root_dir, sid_root_dir = args.sid_root_dir, additional_root_dir = args.additional_root_dir,
     sample_map_path = args.sample_map_path,external_id_key = args.external_id_key)
