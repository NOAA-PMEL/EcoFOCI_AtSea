#!/bin/bash

# Purpose:
#       Script to make missing/qc'd specified variables

cruiseid='NW1701'
cruiseyear='2017'

data_dir="/Users/bell/ecoraid/${cruiseyear}/CTDCasts/${cruiseid}/final_data/ctd/*.nc"
prog_dir="/Users/bell/Programs/Python/EcoFOCI_AtSea/ctd_edit_clutils/"

for files in $data_dir
do
    names=(${files//\// })
    outfile=${names[${#names[@]} - 1]}
    echo "processing file: $files"
    python ${prog_dir}NetCDF_MissingVar.py ${files} CTDOST_4220
    python ${prog_dir}NetCDF_MissingVar.py ${files} CTDOXY_4221
done
