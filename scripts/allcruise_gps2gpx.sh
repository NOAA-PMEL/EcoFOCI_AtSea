#!/bin/bash

# Purpose:
#       Script to run SCS_shptrack2gpx.py for each file in a directory
#       and output as independant files per day

cruiseid='DY1706l3'
cruiseyear='2017'

data_dir="/Volumes/WDC_internal/Users/bell/ecoraid/${cruiseyear}/AlongTrack/${cruiseid}/SCS/GPSGAR17N/*GPGGA*"
prog_dir="/Volumes/WDC_internal/Users/bell/Programs/Python/EcoFOCI_AtSea/"
out_dir="/Volumes/WDC_internal/Users/bell/scratch/"

csv=1
for files in $data_dir
do
    names=(${files//\// })
    outfile=${names[${#names[@]} - 1]}
    echo "processing file: $files"
    if [ ${csv} -eq 0 ]
    then
    	python ${prog_dir}SCS_shptrack2gpx.py -i ${files}  >> ${out_dir}${outfile}.gpx
    else
    	python ${prog_dir}SCS_shptrack2gpx.py -i ${files} -csv >> ${out_dir}${outfile}.csv
   	fi
done
