#!/usr/bin/env python
# Filename: extract_target_imgs 
"""
introduction:

    This script extracts patches with the target in the center base on target polyogns in shapefile.

    It can also perform basic data augmentation (rotations and flips).

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 18 July, 2017
"""


import sys,os,subprocess
from optparse import OptionParser

#pyshp library
import shapefile

# import shapely
from shapely.geometry import Polygon

def get_polygons(shp_path):
    if os.path.isfile(shp_path) is False:
        print('Error, File: %s not exist'%shp_path)
        return False

    try:
        shp_obj = shapefile.Reader(shp_path)
    except IOError:
        print("Read file: %s failed: "%shp_path + str(IOError))
        return False

    if shp_obj.shapeType != 5:
        print('It is not polygon shapefile')
        return False

    shapes_list = shp_obj.shapes()
    return shapes_list


def main(options, args):
    shp_path = args[0]
    image_path = args[1]

    polygons = get_polygons(shp_path)


    pass


if __name__ == "__main__":
    usage = "usage: %prog [options] target_shp image"
    parser = OptionParser(usage=usage, version="1.0 2017-7-15")
    parser.description = 'Introduction: Extract patches based on polygons in shapefile from a large image \n ' \
                         'The image and shape file should have the same projection'
    parser.add_option("-W", "--s_width",
                      action="store", dest="s_width",
                      help="the width of wanted patch")
    parser.add_option("-H", "--s_height",
                      action="store", dest="s_height",
                      help="the height of wanted patch")
    parser.add_option("-o", "--out_dir",
                      action="store", dest="out_dir",
                      help="the folder path for saving output files")

    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 1:
        parser.print_help()
        sys.exit(2)

    # if options.para_file is None:
    #     basic.outputlogMessage('error, parameter file is required')
    #     sys.exit(2)

    main(options, args)
