
import os
from PIL import Image 
import numpy as np

img_path = '../data/100_maps/8628000.jp2'
output_dir = '../data/100_maps_crop/'


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
        img_clip = enlarged_map.crop((idx * shift_size, jdx * shift_size, (idx + 1) * shift_size, (jdx + 1) * shift_size))

        out_path = os.path.join(output_dir, 'h' + str(idx) + '_w' + str(jdx) + '.jpg')
        img_clip.save(out_path)

print('Done cropping %s' %img_path )