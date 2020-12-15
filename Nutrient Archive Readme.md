# Nutrient Archive Readme

Author: S. Bell - shaun.bell (at) noaa.gov
Program: EcoFOCI
Initial Document Date: 2018-07-25

## Purpose:   

This document provides guidance and steps to creating archival nutrient data from CTD profiles for EcoFOCI.  It also provides guidance for creating a "merged" CTD + Nutrient data file for usage and analysis from two independantly archived files (CTD data and Nutrient data).

## Software:

* python 
  + 3.6 or greater **tested**
  + 2.7 (probably work, but untested)

Routines are written in python and tested for 3.6 or greater but may work on version 2.7.  Limited energy will be spent to maintaining 2.7 compatability as it is to be EOL by 2020

* expected that an conda python environment exists.  If using the EcoFOCI server 'pavlof' then you will need to activate the proper environment `source activate py36` or `conda activate py36`.  If using the EcoFOCI server 'akutan' python-3 is the default conda environment.

## Data:

Raw ascii nutrient data as processed/QC'd by E. Wisegarver

Data is expected to be of the format:   

```text 
cast	niskin	PO4 (uM)	Sil (uM)	NO3 (uM)	NO2 (uM)	NH4 (uM)
39	1	1.930	31.2	11.2	0.71	7.61
39	2	1.938	31.5	11.2	0.72	7.78
39	3	1.936	31.3	11.0	0.75	7.74
39	4	1.936	31.0	11.0	0.77	7.80
39	5	1.932	33.2	11.0	0.77	7.65

```

(tab delimited, cast and niskin order do not matter as it will be sorted in the software)

and in order to match niskin and cast information, the *.report_btl file must be used (generated during intial processing of CTD data).

The report file is expected to have the format:

```text 
cast    date    time    nb  Sal00   Sal11   Sbeox0Mm/Kg Sbeox0PS    Sbeox1Mm/Kg Sbeox1PS    Sigma-t00   PrDM    T090C   C0mS/cm T190C   C1mS/cm Sbeox0V Sbeox1V FlECO-AFLTurbWETntu0
ctd036  07-Sep-2016 23:31:06    1   32.3731 32.3750 195.671 62.770  193.262 61.997  25.5671 102.266 5.2335  31.423602   5.2347  31.426318   1.8575  1.6237  0.0451  0.5544
```

Beyond the cast, date, time, nb parameters, no other variables matter as the archive nutrient data will only have the depth info and nutrient info.

Currently CTD data is processed and archived as ctd/\*.nc files and upcast bottle data as btl/\*.nc and both are generated during CTD processing.

### Conversion to Archive format

The archive format for EcoFOCI is netcdf.  Currently the flavor of this has been called the 'EPIC' standard which involves a specific set of 'keys' to identify variables and it uses a dual time word (two variables to describe one time).  This flavor is out of favor and unsupported by the community at large with the exception of PMEL Ferret Software.  The community standard for future development is 'CF/COARDS' flavored netcdf files where the archive has a single timeword specified as '{units of time} since {start date}' eg. 'hours since 1970-01-01'.  Variables will also have standard names when applicable and as comprehensive a description via their meta-data as is possible.  Variable names are still allowed to be defined by the group of interest but should be descriptive as well.

The python routine to do this conversion is `Nut_ncgen.py`

The usage is: 

```text 
usage: Nut_ncgen.py [-h] CruiseID btlpath nutpath output config_file_name

Merge and archive nutrient csv data and bottle data

positional arguments:
  CruiseID          provide the cruiseid
  btlpath           full path to .report_btl
  nutpath           full path to nutrient csv file
  output            full path to output folder (files will be generated there
  config_file_name  full path to config file - nut_config.yaml

optional arguments:
  -h, --help        show this help message and exit
```

and it can be found in the root `README.md` documentation.

Long example of usage:   

```text 
python Nut_ncgen.py DY1707 /full-path-to/dy1707l1.report_btl 
 /full-path-to/DY1707\ Nutrient\ Data.csv 
 /full-path-to/working/ /full-path-to/config_files/nut_uml_epickeys.yaml
```

the `nut_uml_epickeys.yaml` is the file that spells out all of the netcdf metainformation for building variables (but not for adding deployment meta-information).  Any properly constructed file can be used as the configuration setup but the `config_files/nut_uml_epickeys.yaml` is likely the one most relevant until it is replaced with a CF compliant version.

A CF compliant file exists but is being held until 2018 processing (2019) as QC flags still need to be determined.

Content looks as follows: 

``` yaml 
---
NH4_189: 
  name: NH4
  generic_name: NH4
  EPIC_KEY: 189
  units: uM/l
  longname: 'AMMONIUM (micromoles/l)'
NO3_182: 
  name: NO3
  generic_name: NO3
  EPIC_KEY: 182
  units: uM/l
  longname: 'NITRATE (micromoles/l)'
BTL_103: 
  name: BTL
  generic_name: BTL
  EPIC_KEY: 103
  units: ''
  longname: 'NISKIN BOTTLE NUMBER'
SI_188: 
  name: SI
  generic_name: SI
  EPIC_KEY: 188
  units: uM/l
  longname: 'SILICATE (micromoles/l)'
PO4_186: 
  name: PO4
  generic_name: PO4
  EPIC_KEY: 186
  units: uM/l
  longname: 'PHOSPHATE (micromoles/l)'
NO2_184: 
  name: NO2
  generic_name: NO2
  EPIC_KEY: 184
  units: uM/l
  longname: 'NITRITE (micromoles/l)'
```

the user will now have a folder of \*.nc files which can be archived in the {cruise}/final_data/nut/ directory (create it if it doesnt exist and change permissions to 775)

***Creating btl netcdf files uses exactly the same process except the program is `BTL_ncgen.py` ***

**TODO** Document how to add cruise meta-information to files

### Merging with existing {cruise}/final_data/ctd/

Merged files take the existing netcdf ctd data and collocate nutrients at the discrete depths to build a single file for analysis.

The python routine to do this is called `CTDpNUT_ncgen.py`

The usage is:

```text 
positional arguments:
  CruiseID          provide the cruiseid
  ctd_ncpath        ctd netcdf directory
  nut_ncpath        nutrient netcdf directory
  output            full path to output folder (files will be generated there
  config_file_name  full path to config file - ctdpnut_epickeys.yaml

optional arguments:
  -h, --help        show this help message and exit
  -v, --verbose     output messages
  -csv, --csv       output merged data as csv
```

This functions more or less the same as the nut and btl creation routines.  The exceptions are that you only need to pass the directory of the netcd ctd and nut files (it will find and combine the same cast numbers) and that the config_file needs to have all the parameters you wish to have in a merged file.  This may just be the combination of the ctd config file and the nutrient config file.  Finally, a csv option is provided as netcdf files may not be useful to the researcher using combined files

an example of the config file is as follows:

``` yaml
---
Trb_980:
  name: Trb
  generic_name: turb
  EPIC_KEY: 980
  units: FNU
  longname: Turbidity(FNU)
  sbe_label: TurbWETntu0
S_42:
  name: S
  generic_name: sal
  EPIC_KEY: 42
  units: psu
  longname: SALINITY (PSU)
  sbe_label: Sal11
S_41:
  name: S
  generic_name: sal
  EPIC_KEY: 41
  units: psu
  longname: SALINITY (PSU)
  sbe_label: Sal00
CTDOXY_4221:
  name: CTDOXY
  generic_name: ox
  EPIC_KEY: 4221
  units: umol/kg
  longname: OXYGEN (UMOL/KG)
  sbe_label: Sbeox1Mm/Kg
D_3:
  name: D
  generic_name: depth
  EPIC_KEY: 3
  units: m
  longname: DEPTH (M)
  sbe_label: DepSM
T_28:
  name: T
  generic_name: temp
  EPIC_KEY: 28
  units: C
  longname: TEMPERATURE (C)
  sbe_label: T090C
OST_62:
  name: OST
  generic_name: ox
  EPIC_KEY: 62
  units: '%'
  longname: OXYGEN %SAT
  sbe_label: Sbeox0PS
O_65:
  name: O
  generic_name: ox
  EPIC_KEY: 65
  units: umol/kg
  longname: OXYGEN (UMOL/KG)
  sbe_label: Sbeox0Mm/Kg
T2_35:
  name: T2
  generic_name: temp
  EPIC_KEY: 35
  units: C
  longname: Secondary Temperature
  sbe_label: T190C
BTL_103:
  name: BTL
  generic_name: btl
  EPIC_KEY: 103
  units: 
  longname: NISKIN BOTTLE NUMBER
  sbe_label: nb
PAR_905:
  name: PAR
  generic_name: par
  EPIC_KEY: 905
  units: uEin m-2 s-1
  longname: Photosynthetic Active Radiation
  sbe_label: Par
F_903:
  name: F
  generic_name: f
  EPIC_KEY: 903
  units: mg m-3
  longname: Fluorometer (CTD)
  sbe_label: FlECO-AFL
CTDOST_4220:
  name: CTDOST
  generic_name: ox
  EPIC_KEY: 4220
  units: '%'
  longname: OXYGEN %SAT
  sbe_label: Sbeox1PS
ST_70:
  name: ST
  generic_name: den
  EPIC_KEY: 70
  units: kg m-3
  longname: SIGMA-T (KG/M**3)
  sbe_label: Sigma-t00
STH_71:
  name: STH
  generic_name: potden
  EPIC_KEY: 71
  units: kg m-3
  longname: SIGMA-THETA (KG/M**3)
  sbe_label:  
Trb_980:
  name: Trb
  generic_name: turb
  EPIC_KEY: 980
  units: FNU
  longname: Turbidity(FNU)
  sbe_label:  
NH4_189: 
  name: NH4
  generic_name: NH4
  EPIC_KEY: 189
  units: uM/l
  longname: 'AMMONIUM (micromoles/l)'
NO3_182: 
  name: NO3
  generic_name: NO3
  EPIC_KEY: 182
  units: uM/l
  longname: 'NITRATE (micromoles/l)'
BTL_103: 
  name: BTL
  generic_name: BTL
  EPIC_KEY: 103
  units: ''
  longname: 'NISKIN BOTTLE NUMBER'
SI_188: 
  name: SI
  generic_name: SI
  EPIC_KEY: 188
  units: uM/l
  longname: 'SILICATE (micromoles/l)'
PO4_186: 
  name: PO4
  generic_name: PO4
  EPIC_KEY: 186
  units: uM/l
  longname: 'PHOSPHATE (micromoles/l)'
NO2_184: 
  name: NO2
  generic_name: NO2
  EPIC_KEY: 184
  units: uM/l
  longname: 'NITRITE (micromoles/l)'
```

input and output variable names must be the same (thats the unindented names in the structure above)
the `sbe_label` tag is only relevant for making the btl and ctd files from sbe files and can be ignored here.

## Document History:

V1 - 2018-07-25 - Document Creation
