#!/usr/bin/env python
# Filename: split_image 
"""
introduction: split a large image to many separate patches

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 15 July, 2017
"""
import sys,os,subprocess
from optparse import OptionParser

def sliding_window(image_width,image_height, patch_w,patch_h):
    count_x = int(image_width)/int(patch_w)
    count_y = int(image_height)/int(patch_h)

    leftW = int(image_width)%int(patch_w)
    leftH = int(image_height)%int(patch_h)
    if leftW < patch_w/3:
        # count_x = count_x - 1
        leftW = patch_w + leftW
    else:
        count_x = count_x + 1
    if leftH < patch_h/3:
        # count_y = count_y - 1
        leftH = patch_h + leftH
    else:
        count_y = count_y + 1

    patch_boundary = []
    for i in range(0,count_x):
        for j in range(0,count_y):
            w = patch_w
            h = patch_h
            if i==count_x -1:
                w = leftW
            if j == count_y - 1:
                h = leftH
            new_patch = (i*patch_w, j*patch_h,w, h)
            patch_boundary.append(new_patch)

    return patch_boundary



def split_image(input,output_dir,patch_w=1024,patch_h=1024):
    """
    split a large image to many separate patches
    Args:
        input: the input big images
        output_dir: the folder path for saving output files
        patch_w: the width of wanted patch
        patch_h: the height of wanted patch

    Returns: True is successful, False otherwise

    """
    if os.path.isfile(input) is False:
        print("Error: %s file not exist"%input)
        return False
    if os.path.isdir(output_dir) is False:
        print("Error: %s Folder not exist" % input)
        return False

    Size_str = os.popen('gdalinfo '+input + ' |grep Size').readlines()
    temp = Size_str[0].split()
    img_witdh = int(temp[2][0:len(temp[2])-1])
    img_height = int(temp[3])

    print('input Width %d  Height %d'%(img_witdh,img_height))

    patch_boundary = sliding_window(img_witdh,img_height,patch_w,patch_h)

    index = 0
    pre_name = os.path.splitext(os.path.basename(input))[0]
    for patch in patch_boundary:
        # print information
        print(patch)
        output_path = os.path.join(output_dir,pre_name+'_p_%d.tif'%index)
        args_list = ['gdal_translate','-srcwin',str(patch[0]),str(patch[1]),str(patch[2]),str(patch[3]), input, output_path]
        ps = subprocess.Popen(args_list)
        returncode = ps.wait()
        if os.path.isfile(output_path) is False:
            print('Failed in gdal_translate, return codes: ' + str(returncode))
            return False
        index = index + 1



def main(options, args):
    if options.s_width is None:
        patch_width = 1024
    else:
        patch_width = int(options.s_width)
    if options.s_height is None:
        patch_height = 1024
    else:
        patch_height = int(options.s_width)

    if options.out_dir is None:
        out_dir = "./"
    else:
        out_dir = options.out_dir

    image_path = args[0]

    split_image(image_path,out_dir,patch_width,patch_height)


    pass

if __name__ == "__main__":
    usage = "usage: %prog [options] image_path"
    parser = OptionParser(usage=usage, version="1.0 2017-7-15")
    parser.description = 'Introduction: split a large image to many separate parts '
    parser.add_option("-W", "--s_width",
                      action="store", dest="s_width",
                      help="the width of wanted patches")
    parser.add_option("-H", "--s_height",
                      action="store", dest="s_height",
                      help="the height of wanted patches")
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