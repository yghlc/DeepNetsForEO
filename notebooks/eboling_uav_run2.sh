#!/bin/bash

### This dataset contains orthoimages (top/ folder) and ground truthes (gts_for_participants/) folder

###pre-process UAV images
#./extract_target_imgs.py -n 255 /home/hlc/Data/eboling/training_validation_data/gps_rtk/gps_rtk_polygons_3_fix.shp /home/hlc/Data/eboling/eboling_uav_images/dom/UAV_DOM_Eboling_0.48m.tif  -o /home/hlc/Data/eboling/eboling_uav_images/dom/EbolingUAV_DeepNetEO_2/top 
#./extract_target_imgs.py -n 5 /home/hlc/Data/eboling/training_validation_data/gps_rtk/gps_rtk_polygons_3_fix.shp /home/hlc/Data/eboling/eboling_uav_images/dom/raster_class_version_gps_rtk_3_fix.tif  -o /home/hlc/Data/eboling/eboling_uav_images/dom/EbolingUAV_DeepNetEO_2/gts_numpy


### transform the ground truth 2D matrices(label as 1,2,3) to  RGB-encoded images 
#./convert_gt.py /home/hlc/Data/eboling/eboling_uav_images/dom/EbolingUAV_DeepNetEO_2/gts_numpy/*.tif --to-color --out /home/hlc/Data/eboling/eboling_uav_images/dom/EbolingUAV_DeepNetEO_2/gts_for_participants

### Extract small patches from the tiles to create the train and test sets
#./extract_images.py

### the extracted images to LMDB
#./create_lmdb.py

### training
#./training.py --niter 40000 --update 1000 --init vgg16weights.caffemodel --snapshot trained_network_weights/

#./training.py --niter 40000 --update 1000 --init /home/hlc/Data/DeepNetsForEO_test/pre-train/segnet_vaihingen_128x128_fold1_iter_60000.caffemodel --snapshot trained_network_weights/

#./training.py --niter 40000 --update 1000 --init /home/hlc/Data/DeepNetsForEO_test/pre-train/potsdam_rgb_128_fold1_iter_80000.caffemodel --snapshot trained_network_weights/

### inference
./inference.py 0 1 2 3 4 5 6 7 8 9 10 11 12 13 --weights snapshots/_iter_40000.caffemodel 
