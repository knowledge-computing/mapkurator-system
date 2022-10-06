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

def main(args):

    jp2_root_dir = args.jp2_root_dir
    sid_root_dir = args.sid_root_dir
    additional_root_dir = args.additional_root_dir
    out_geotiff_dir = args.out_geotiff_dir

    sample_map_path = args.sample_map_path
    external_id_key = args.external_id_key

    jp2_file_path_list = glob.glob(os.path.join(jp2_root_dir, '*/*.jp2'))
    sid_file_path_list = glob.glob(os.path.join(sid_root_dir, '*.jpg')) # use converted jpg directly
    add_file_path_list = glob.glob(os.path.join(additional_root_dir, '*'))

    jp2_file_fullpath_dict = func_file_to_fullpath_dict(jp2_file_path_list) 
    sid_file_fullpath_dict = func_file_to_fullpath_dict(sid_file_path_list) 
    add_file_fullpath_dict = func_file_to_fullpath_dict(add_file_path_list) 

    sample_map_df = pd.read_csv(sample_map_path, dtype={'external_id':str})


    for index, record in sample_map_df.iterrows():
        external_id = record.external_id
        transform_method = record.transformation_method
        gcps = record.gcps
        filename_without_extension = external_id.strip("'").replace('.','')

        full_path = ''
        if filename_without_extension in jp2_file_fullpath_dict:
            full_path = jp2_file_fullpath_dict[filename_without_extension]
        elif filename_without_extension in sid_file_fullpath_dict:
            full_path = sid_file_fullpath_dict[filename_without_extension]
        elif filename_without_extension in add_file_fullpath_dict:
            full_path = add_file_fullpath_dict[filename_without_extension]
        else:
            print('image with external_id not found in image_dir:', external_id)
            continue
        assert (len(full_path)!=0)

        gcps = ast.literal_eval(gcps)

        gcp_str = ''
        for gcp in gcps:
            lng, lat = gcp['location']
            x, y = gcp['pixel']
            gcp_str += '-gcp '+str(x) + ' ' + str(y) + ' ' + str(lng) + ' ' + str(lat) + ' '
        
        # gdal_translate to add GCP to raw image
        gdal_command = 'gdal_translate -of Gtiff '+gcp_str + full_path + ' ' + os.path.join(out_geotiff_dir, filename_without_extension) + '_temp.geotiff'
        print(gdal_command)
        os.system(gdal_command)
        
        
        assert transform_method in ['affine','polynomial','tps']
             
        # reprojection with gdal_warp
        if transform_method == 'affine': 
            # first order
            
            warp_command = 'gdalwarp -s_srs EPSG:4326 -t_srs EPSG:3857 -r near -order 1 -of GTiff ' + os.path.join(out_geotiff_dir, filename_without_extension) + '_temp.geotiff' + ' ' + os.path.join(out_geotiff_dir, filename_without_extension) + '.geotiff'  
            
        elif transform_method == 'polynomial':
            # second order
            warp_command = 'gdalwarp -s_srs EPSG:4326 -t_srs EPSG:3857 -r near -order 2 -of GTiff '+ os.path.join(out_geotiff_dir, filename_without_extension) + '_temp.geotiff' + ' ' + os.path.join(out_geotiff_dir, filename_without_extension) + '.geotiff'  

        elif transform_method == 'tps':
            # Thin plate spline #debug/11558008.geotiff  #10057000.geotiff
            warp_command = 'gdalwarp -s_srs EPSG:4326 -t_srs EPSG:3857  -r near -tps -of GTiff '+ os.path.join(out_geotiff_dir, filename_without_extension) + '_temp.geotiff' + ' ' + os.path.join(out_geotiff_dir, filename_without_extension) + '.geotiff'  
            
        else:
            raise NotImplementedError
        print(warp_command)
        os.system(warp_command)
        # remove temporary tiff file
        # os.system('rm ' + os.path.join(out_geotiff_dir, filename_without_extension) + '_temp.geotiff')


        logging.info('Done generating geotiff for %s', external_id)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--jp2_root_dir', type=str, default='/data/rumsey-jp2/',
                        help='image dir of jp2 files.')
    parser.add_argument('--sid_root_dir', type=str, default='/data2/rumsey_sid_to_jpg/',
                        help='image dir of sid files.')
    parser.add_argument('--additional_root_dir', type=str, default='/data2/rumsey-luna-img/',
                        help='image dir of additional luna files.')
    parser.add_argument('--out_geotiff_dir', type=str, default='data/geotiff/',
                        help='output dir for geotiff')
    parser.add_argument('--sample_map_path', type=str, default='data/initial_US_100_maps.csv',
                        help='path to sample map csv, which contains gcps info')
    parser.add_argument('--external_id_key', type=str, default='external_id',
                        help='key string for external id, could be external_id or ListNo')
 
    args = parser.parse_args()
    print(args)


    main(args)
