#!/bin/bash

### run test
### This dataset contains orthoimages (top/ folder) and ground truthes (gts_for_participants/) folder

### transform the ground truth RGB-encoded images to 2D matrices (also image, but labeled as 1,2,3..)
#./convert_gt.py /home/hlc/Data/DeepNetsForEO_test/Vaihingen/gts_for_participants/*.tif --from-color --out /home/hlc/Data/DeepNetsForEO_test/Vaihingen/gts_numpy


### Extract small patches from the tiles to create the train and test sets
#./extract_images.py

### the extracted images to LMDB
#./create_lmdb.py

### training
#./training.py --niter 40000 --update 1000 --init vgg16weights.caffemodel --snapshot trained_network_weights/

#./training.py --niter 40000 --update 1000 --init /home/hlc/Data/DeepNetsForEO_test/pre-train/segnet_vaihingen_128x128_fold1_iter_60000.caffemodel --snapshot trained_network_weights/

./inference.py 32 1 --weights snapshots/_iter_40000.caffemodel 
