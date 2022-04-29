import os
import glob
import pandas as pd
import pdb

jp2_root_dir = '/data/rumsey-jp2/'
sid_root_dir = '/data/rumsey-sid/'
#omo_csv_path = '../metadata/davidrumsey/davidrumsey_metadata.csv'
sample_map_path = 'data/initial_US_100_maps.csv'
external_id_key = 'external_id'

# hacked the external_id

def func_file_to_fullpath_dict(file_path_list):

    file_fullpath_dict = dict()
    for file_path in file_path_list:
        file_fullpath_dict[os.path.basename(file_path)] = file_path

jp2_file_path_list = glob.glob(os.path.join(jp2_root_dir, '*/*.jp2'))
sid_file_path_list = glob.glob(os.path.join(sid_root_dir, '*/*.sid'))

jp2_file_fullpath_dict = func_file_to_fullpath_dict(jp2_file_path_list) 
sid_file_fullpath_dict = func_file_to_fullpath_dict(sid_file_path_list) 

#omo_df = pd.read_csv(omo_csv_path)
sample_map_df = pd.read_csv(sample_map_path)


# # match omo_df with sample_map_df
# # hack for external_id
# for external_id in sample_map_df[external_id_key]:
#     if external_id == 3389.007:
#         pdb.set_trace()
#     if len(omo_df[omo_df.external_id == str(external_id)]) == 0:
#         print('External ID in sample map list not found in OMO metadata', external_id)
#     else:
#         omo_df[omo_df.external_id == str(external_id)]
        

for index, record in sample_map_df.iterrows():
    external_id = record.external_id
    gcp = record.gcps
    pdb.set_trace()

print('done')