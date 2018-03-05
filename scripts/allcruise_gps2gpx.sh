#!/bin/bash

# Purpose:
#       Script to run SCS_shptrack2gpx.py for each file in a directory
#       and output as independant files per day

cruiseid='DY1705'
cruiseyear='2017'

data_dir="/Users/bell/ecoraid/${cruiseyear}/AlongTrack/${cruiseid}/SCS/GPSGAR17N/*GPGGA*"
prog_dir="/Users/bell/Programs/Python/EcoFOCI_AtSea/"
out_dir="/Users/bell/scratch/"

for files in $data_dir
do
    names=(${files//\// })
    outfile=${names[${#names[@]} - 1]}
    echo "processing file: $files"
    python ${prog_dir}SCS_shptrack2gpx.py -i ${files}  >> ${out_dir}${outfile}.gpx
done
