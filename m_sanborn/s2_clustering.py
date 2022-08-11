import os
import json
import argparse
from sklearn.cluster import DBSCAN
from matplotlib import pyplot as plt
import geopandas as gpd
import pandas as pd
from bs4 import BeautifulSoup
from mpl_toolkits.basemap import Basemap
from pyproj import Proj, transform

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import numpy as np
from shapely.geometry import MultiPoint
from geopy.distance import great_circle


county_index_dict = {'Cuyahoga County (OH)': 193,
 'Fulton County (GA)': 73,
 'Kern County (CA)': 2872,
 'Lancaster County (NE)': 1629,
 'Los Angeles County (CA)': 44,
 'Mexico': -1,
 'Nevada County (CA)': 46,
 'New Orleans (LA)': -1,
 'Pima County (AZ)': 2797,
 'Placer County (CA)': 1273,
 'Providence County (RI)\xa0': 1124,
 'Saint Louis (MO)': -1,
 'San Francisco County (CA)': 1261,
 'San Joaquin County (CA)': 1213,
 'Santa Clara (CA)': 48,
 'Santa Cruz (CA)': 2386,
 'Suffolk County (MA)': 272,
 'Tulsa County (OK)': 526,
 'Washington County (AK)': -1,
 'Washington DC': -1}

def get_centermost_point(cluster):
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
    return tuple(centermost_point)

def clustering_func(lat_list, lng_list):
    X = [[a,b] for a,b in zip(lat_list, lng_list)]
    coords = np.array(X)
    
    # https://geoffboeing.com/2014/08/clustering-to-reduce-spatial-data-set-size/
    kms_per_radian = 6371.0088
    epsilon = 1.5 / kms_per_radian
    db = DBSCAN(eps=epsilon, min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
    cluster_labels = db.labels_
    num_clusters = len(set(cluster_labels))
    clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters)])
    
    centermost_points = get_centermost_point(clusters[0])
    return centermost_points


def clustering(args):
    dataset_name = args.dataset_name
    geocoding_name = args.geocoding_name

    sanborn_output_dir = '/data2/sanborn_maps_output'

    input_dir=os.path.join(sanborn_output_dir, dataset_name, 'geocoding_suffix_testr', geocoding_name)
    output_dir = os.path.join(sanborn_output_dir, dataset_name, 'clustering_testr', geocoding_name)
    county_boundary_path = '/home/zekun/Sanborn/cb_2018_us_county_500k/cb_2018_us_county_500k.shp'

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    inProj = Proj(init='epsg:3857')
    outProj = Proj(init='epsg:4326')

    county_boundary_df = gpd.read_file(county_boundary_path)

    if dataset_name == 'LoC_sanborn':
        metadata_tsv_path = '/home/zekun/Sanborn/Sheet_List.tsv'
        meta_df = pd.read_csv(metadata_tsv_path, sep='\t')

    file_list = os.listdir(input_dir)

    out_dict = dict()
    for file_path in file_list:
        
        map_name = os.path.basename(file_path).split('.')[0]
        if dataset_name == 'LoC_sanborn':
            county_name = meta_df[meta_df['filename'] == map_name]['County'].values[0]
        elif dataset_name == 'LA_sanborn':
            county_name = 'Los Angeles County (CA)'
        else:
            raise NotImplementedError

        index = county_index_dict[county_name]
        if index >= 0:
            poly_geometry = county_boundary_df.iloc[index].geometry
        
        
        with open(os.path.join(input_dir,file_path), 'r') as f:
            data = f.readlines()
            
        lat_list = []
        lng_list = []
        for line in data:
            if line[0:5].strip() == 'null':
                continue
                
            line_dict = json.loads(line)
            
            if 'lat' not in line_dict or 'lng' not in line_dict:
                #print(line_dict)
                continue 
            lat = float(line_dict['lat'])
            lng = float(line_dict['lng'])
            
            point = Point(lng, lat)
            
            if index >= 0:
                if point.within(poly_geometry): # geocoding point within county boundary
                    lat_list.append(lat)
                    lng_list.append(lng)
                else:
                    pass
            else: # cluster based on all results
                lat_list.append(lat)
                lng_list.append(lng)
            
        if len(lat_list) >0 and len(lng_list) > 0:
            pred = clustering_func(lat_list, lng_list)
            # print(pred)
        else:
            print('No data to cluster')

        print(map_name, pred)
        out_dict[map_name] = pred

    with open(os.path.join(output_dir, 'pred_center.json'),'w') as f:
        json.dump(out_dict, f)

        # raster io get center
            
        # title = dataset_name + '-' + geocoding_name + '-' + file_path[:-5]
        
        # if dataset_name == 'LoC_sanborn':
        #     loc_sanborn_dir = '/data2/sanborn_maps/Sanborn100_Georef/'
        #     xml_path = os.path.join(loc_sanborn_dir,file_path[:-5] + '.tif.aux.xml')
        #     try:
        #         with open(xml_path) as fp:
        #             soup = BeautifulSoup(fp)
                
        #         target_gcp_list = soup.findAll("metadata")[1].targetgcps.findAll("double")
        #     except Exception as e:
        #         print(xml_path)
        #         continue
            
        #     xy_list = []
        #     for target_gcp in target_gcp_list:
        #         xy_list.append(float(target_gcp.contents[0]))
                
        #     x_list = xy_list[0::2]
        #     y_list = xy_list[1::2]
            
        #     lng2_list,  lat2_list = [],[]
        #     for x1,y1 in zip(x_list, y_list):
        #         x2,y2 = transform(inProj,outProj,x1,y1)
        #         #print (x2,y2)
        #         lng2_list.append(x2)
        #         lat2_list.append(y2)
                
        

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--dataset_name', type=str, default=None,
        choices=['LA_sanborn', 'LoC_sanborn'],
        help='dataset name, same as expt_name')
    parser.add_argument('--geocoding_name', type=str, default=None, 
        choices=['google','arcgis','geonames'],
        help='geocoder name')
 
    
    # parser.add_argument('--output_folder', type=str, default='/data2/sanborn_maps_output/LA_sanborn/geocoding/')
    # parser.add_argument('--input_map_geojson_path', type=str, default='/data2/sanborn_maps_output/LA_sanborn/geojson_testr/service-gmd-gmd436m-g4364m-g4364lm-g4364lm_g00656189401-00656_01_1894-0001l.geojson')
    # parser.add_argument('--api_key', type=str, default=None, help='Specify API key if needed')
    # parser.add_argument('--user_name', type=str, default=None, help='Specify user name if needed')

    # parser.add_argument('--suffix', type=str, default=None, help='placename suffix (e.g. city name)')
    
    # parser.add_argument('--max_results', type=int, default=5, help='max number of results returend by geocoder')

    # parser.add_argument('--geocoder_option', type=str, default='arcgis', 
    #     choices=['arcgis', 'google','geonames'], 
    #     help='Select text spotting model option from ["arcgis","google","geonames"]') # select text spotting model

                        
    args = parser.parse_args()
    print('\n')
    print(args)
    print('\n')
    
    clustering(args)


if __name__ == '__main__':

    main()
