import os
import glob
import pandas as pd
import ast
import argparse
import logging
import pdb

logging.basicConfig(level=logging.INFO)

def func_file_to_fullpath_dict(file_path_list):

    file_fullpath_dict = dict()
    for file_path in file_path_list:
        file_fullpath_dict[os.path.basename(file_path).split('.')[0]] = file_path

    return file_fullpath_dict  

def get_img_path_from_external_id(jp2_root_dir = '/data/rumsey-jp2/', sid_root_dir = '/data/rumsey-sid/', additional_root_dir='/data2/rumsey-luna-img/', sample_map_path = None,external_id_key = 'external_id') :
    # returns (1) a dict with external-id as key, full image path as value (2) list of external-id that can not find image path

    jp2_file_path_list = glob.glob(os.path.join(jp2_root_dir, '*/*.jp2'))
    sid_file_path_list = glob.glob(os.path.join(sid_root_dir, '*/*.sid'))
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

def get_img_path_from_external_id_and_image_no(jp2_root_dir = '/data/rumsey-jp2/', sid_root_dir = '/data/rumsey-sid/', additional_root_dir='/data2/rumsey-luna-img/', sample_map_path = None,external_id_key = 'external_id') :
    # returns (1) a dict with external-id as key, full image path as value (2) list of external-id that can not find image path

    jp2_file_path_list = glob.glob(os.path.join(jp2_root_dir, '*/*.jp2'))
    sid_file_path_list = glob.glob(os.path.join(sid_root_dir, '*/*.sid'))
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
    parser.add_argument('--sid_root_dir', type=str, default='/data/rumsey-sid/',
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
