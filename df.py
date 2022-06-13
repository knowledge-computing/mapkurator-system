
import pandas as pd 
import pdb 

sample_map_path = 'sample_map_lists/luna_omo_metadata_41721_1000_sample.csv'
sample_map_df = pd.read_csv(sample_map_path, dtype={'external_id':str})
for index, record in sample_map_df.iterrows():
    # if index < 180:
    #     continue 
    print(index, record.external_id)
    if index >= 180:
        pdb.set_trace()