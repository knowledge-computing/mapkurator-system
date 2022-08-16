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

def plot_points(lat_list, lng_list, target_lat_list=None, target_lng_list = None, pred_lat=None, pred_lng = None, title = None):
    
    plt.figure(figsize=(10,6))
    plt.title(title)
    
    plt.scatter(lng_list, lat_list, marker='o', c = 'violet', alpha=0.5)
    if pred_lat is not None and pred_lng is not None:
        plt.scatter(pred_lng, pred_lat, marker='o', c = 'red')
    
    if target_lat_list is not None and target_lng_list is not None:
        plt.scatter(target_lng_list, target_lat_list, 10, c = 'blue')
    plt.show()

def plot_points_basemap(lat_list, lng_list, target_lat_list=None, target_lng_list = None, pred_lat=None, pred_lng = None, title = None):
    
    plt.figure(figsize=(10,6))
    plt.title(title)
    
    if len(lat_list) >0 and len(lng_list) > 0:
        anchor_lat, anchor_lng = lat_list[0], lng_list[0]
    elif target_lat_list is not None:
        anchor_lat, anchor_lng = target_lat_list[0], target_lng_list[0]
    else:
        anchor_lat, anchor_lng = 45, -100
        
    m = Basemap(projection='lcc', resolution=None,
            width=8E4, height=8E4, 
            lat_0=anchor_lat, lon_0=anchor_lng)
    m.etopo(scale=0.5, alpha=0.5)
    # m.arcgisimage(service='ESRI_Imagery_World_2D', xpixels = 2000, verbose= True)
    # m.arcgisimage(service='ESRI_Imagery_World_2D',scale=0.5, alpha=0.5)
    # m.arcgisimage(service='ESRI_Imagery_World_2D', xpixels = 2000, verbose= True)
    
    lng_list, lat_list = m(lng_list, lat_list)  # transform coordinates
    plt.scatter(lng_list, lat_list, marker='o', c = 'violet', alpha=0.5)
    
    
    if target_lat_list is not None and target_lng_list is not None:
        target_lng_list, target_lat_list = m(target_lng_list, target_lat_list) 
        plt.scatter(target_lng_list, target_lat_list,  marker='o', c = 'blue',edgecolor='blue')
        
    if pred_lat is not None and pred_lng is not None:
        pred_lng, pred_lat = m(pred_lng, pred_lat) 
        plt.scatter(pred_lng, pred_lat, marker='o', c = 'red', edgecolor='black')
        
    plt.show()

def plotting_func(loc_sanborn_dir, pred_dict, lat_lng_dict, dataset_name, geocoding_name):

    for map_name, pred in pred_dict.items():
        
        title = dataset_name + '-' + geocoding_name + '-' + map_name
        lat_list = lat_lng_dict[map_name]['lat_list']
        lng_list = lat_lng_dict[map_name]['lng_list']
        
        if dataset_name == 'LoC_sanborn':
            xml_path = os.path.join(loc_sanborn_dir,map_name + '.tif.aux.xml')
            try:
                with open(xml_path) as fp:
                    soup = BeautifulSoup(fp)
                
                target_gcp_list = soup.findAll("metadata")[1].targetgcps.findAll("double")
            except Exception as e:
                print(xml_path)
                continue
            
            xy_list = []
            for target_gcp in target_gcp_list:
                xy_list.append(float(target_gcp.contents[0]))
                
            x_list = xy_list[0::2]
            y_list = xy_list[1::2]
            
            lng2_list,  lat2_list = [],[]
            for x1,y1 in zip(x_list, y_list):
                x2,y2 = transform(inProj,outProj,x1,y1)
                #print (x2,y2)
                lng2_list.append(x2)
                lat2_list.append(y2)
                
            plot_points(lat_list, lng_list, lat2_list, lng2_list, pred_lat = pred[0], pred_lng = pred[1], title=title)
        else:
            plot_points(lat_list, lng_list,pred_lat = pred[0], pred_lng = pred[1], title=title)
        

def clustering(args):
    dataset_name = args.dataset_name
    geocoding_name = args.geocoding_name
    remove_duplicate_location = args.remove_duplicate_location
    visualize = args.visualize

    sanborn_output_dir = '/data2/sanborn_maps_output'

    input_dir=os.path.join(sanborn_output_dir, dataset_name, 'geocoding_suffix_testr', geocoding_name)
    if remove_duplicate_location:
        output_dir = os.path.join(sanborn_output_dir, dataset_name, 'clustering_testr_removeduplicate', geocoding_name)
    else:
        output_dir = os.path.join(sanborn_output_dir, dataset_name, 'clustering_testr', geocoding_name)
        
    county_boundary_path = '/home/zekun/Sanborn/cb_2018_us_county_500k/cb_2018_us_county_500k.shp'

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    inProj = Proj(init='epsg:3857')
    outProj = Proj(init='epsg:4326')

    county_boundary_df = gpd.read_file(county_boundary_path)

    if dataset_name == 'LoC_sanborn':
        loc_sanborn_dir = '/data2/sanborn_maps/Sanborn100_Georef/' # for comparing with GT
        metadata_tsv_path = '/home/zekun/Sanborn/Sheet_List.tsv'
        meta_df = pd.read_csv(metadata_tsv_path, sep='\t')

    file_list = os.listdir(input_dir)

    pred_dict = dict()
    lat_lng_dict = dict()
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
            geocoding_dict = line_dict['geocoding']
            text = line_dict['text']
            score = line_dict['score']
            geometry = line_dict['geometry']

            if geocoding_dict is None:
                continue # if no geolocation returned by geocoder, then skip 
            
            if 'lat' not in geocoding_dict or 'lng' not in geocoding_dict:
                #print(geocoding_dict)
                continue 
            lat = float(geocoding_dict['lat'])
            lng = float(geocoding_dict['lng'])
            
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

        if remove_duplicate_location:
            lat_list = list(set(lat_list))
            lng_list = list(set(lng_list))
            
        if len(lat_list) >0 and len(lng_list) > 0:
            pred = clustering_func(lat_list, lng_list)
            # print(pred)
        else:
            print('No data to cluster')

        print(map_name, pred)
        pred_dict[map_name] = pred
        lat_lng_dict[map_name]={'lat_list':lat_list, 'lng_list':lng_list}

    if visualize:
        plotting_func(loc_sanborn_dir = loc_sanborn_dir, pred_dict = pred_dict, lat_lng_dict = lat_lng_dict,
            dataset_name = dataset_name, geocoding_name = geocoding_name)

    with open(os.path.join(output_dir, 'pred_center.json'),'w') as f:
        json.dump(pred_dict, f)
        

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--dataset_name', type=str, default=None,
        choices=['LA_sanborn', 'LoC_sanborn'],
        help='dataset name, same as expt_name')
    parser.add_argument('--geocoding_name', type=str, default=None, 
        choices=['google','arcgis','geonames','osm'],
        help='geocoder name')
    parser.add_argument('--visualize', default = False, action = 'store_true') # Enable this when in notebook
    parser.add_argument('--remove_duplicate_location', default=False, action='store_true') # whether remove duplicate geolocations for clustering
    
    # parser.add_argument('--output_folder', type=str, default='/data2/sanborn_maps_output/LA_sanborn/geocoding/')
    # parser.add_argument('--input_map_geojson_path', type=str, default='/data2/sanborn_maps_output/LA_sanborn/geojson_testr/service-gmd-gmd436m-g4364m-g4364lm-g4364lm_g00656189401-00656_01_1894-0001l.geojson')
   
                        
    args = parser.parse_args()
    print('\n')
    print(args)
    print('\n')
    
    clustering(args)


if __name__ == '__main__':

    main()
