
def get_city_suffix(map_df, map_name):
    map_df[map_df['file_name'] == map_name]['City'].values[0]

