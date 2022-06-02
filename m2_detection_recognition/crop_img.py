import sys
import os
from PIL import Image 
import numpy as np
import argparse
import logging

logging.basicConfig(level=logging.INFO)
Image.MAX_IMAGE_PIXELS=None # allow reading huge images

def main(args):

    img_path = args.img_path
    output_dir = args.output_dir

    map_name = os.path.basename(img_path).split('.')[0] # get the map name without extension
    output_dir = os.path.join(output_dir, map_name)

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    map_img = Image.open(img_path) 
    width, height = map_img.size 

    #print(width, height)

    shift_size = 1000

    # pad the image to the size divisible by shift-size
    num_tiles_w = int(np.ceil(1. * width / shift_size))
    num_tiles_h = int(np.ceil(1. * height / shift_size))
    enlarged_width = int(shift_size * num_tiles_w)
    enlarged_height = int(shift_size * num_tiles_h)

    enlarged_map = Image.new(mode="RGB", size=(enlarged_width, enlarged_height))
    # paste map_imge to enlarged_map
    enlarged_map.paste(map_img)

    for idx in range(0, num_tiles_h):
        for jdx in range(0, num_tiles_w):
            img_clip = enlarged_map.crop((jdx * shift_size, idx * shift_size,(jdx + 1) * shift_size, (idx + 1) * shift_size, ))

            out_path = os.path.join(output_dir, 'h' + str(idx) + '_w' + str(jdx) + '.jpg')
            img_clip.save(out_path)

    logging.info('Done cropping %s' %img_path )


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--img_path', type=str, default='../data/100_maps/8628000.jp2',
                        help='path to image file.')
    parser.add_argument('--output_dir', type=str, default='../data/100_maps_crop/',
                        help='path to output dir')
   
    args = parser.parse_args()
    print(args)

    
    # if not os.path.isdir(args.output_dir):
    #     os.makedirs(args.output_dir)
    #     print('created dir',args.output_dir)

    main(args)
