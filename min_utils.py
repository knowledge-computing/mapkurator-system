
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--geojson_dir', type=str, default='data/100_maps_geojson_abc/',
                        help='dir to map input geojson files.')
    parser.add_argument('--gt_dir', type=str, default='',
                        help='dir to ground-truth annotation files.')
    #parser.add_argument('--output_dir', type=str, default='',
    #                    help='path to output evaluation scores')
    parser.add_argument('--shift_size', type=int, default = 1000,
                        help='image patch size and shift size.')
   
    args = parser.parse_args()
    print(args)

    main(args)
