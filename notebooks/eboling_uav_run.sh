#!/bin/bash

### run test
### This dataset contains orthoimages (top/ folder) and ground truthes (gts_for_participants/) folder

### transform the ground truth 2D matrices(label as 1,2,3) to  RGB-encoded images 
#./convert_gt.py /home/hlc/Data/eboling/eboling_uav_images/dom/EbolingUAV/gts_numpy/*.tif --to-color --out /home/hlc/Data/eboling/eboling_uav_images/dom/EbolingUAV/gts_for_participants


###pre-process UAV images
#./split_image.py -W 1200 -H 1200 -o /home/hlc/Data/eboling/eboling_uav_images/dom/EbolingUAV/top /home/hlc/Data/eboling/eboling_uav_images/dom/EbolingUAV/UAV_DOM_Eboling_0.48m_Version2_subset.tif
#./split_image.py -W 1200 -H 1200 -o /home/hlc/Data/eboling/eboling_uav_images/dom/EbolingUAV/gts_numpy /home/hlc/Data/eboling/eboling_uav_images/dom/EbolingUAV/raster_class_version_2_onlyGully_subset.tif


### Extract small patches from the tiles to create the train and test sets
#./extract_images.py

### the extracted images to LMDB
#./create_lmdb.py

### training
#./training.py --niter 40000 --update 1000 --init vgg16weights.caffemodel --snapshot trained_network_weights/

#./training.py --niter 40000 --update 1000 --init /home/hlc/Data/DeepNetsForEO_test/pre-train/segnet_vaihingen_128x128_fold1_iter_60000.caffemodel --snapshot trained_network_weights/

./training.py --niter 40000 --update 1000 --init /home/hlc/Data/DeepNetsForEO_test/pre-train/potsdam_rgb_128_fold1_iter_80000.caffemodel --snapshot trained_network_weights/

### inference
./inference.py 0 1 2 3 4 5 6 7 8 9 --weights snapshots/_iter_40000.caffemodel 
