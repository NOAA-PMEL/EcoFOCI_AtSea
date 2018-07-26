README
------
Collection of utilites for processing and visualizing common data that is gathered during field cruises.

- SCS Data
- CTD Data
- UnderWay Data   

### CTD Basic Editing Utilities
#### Interp2SFC
- extrapolate all variables to surface from chosen depth and resave.


### EPIC/CF netcdf generation
**TODO:**
- From discrete Oxygen/Salinity Calibration/Characterization measurements
- Add CF/COARDS netCDF routines

##### Nutrient netcdf archive instructions
- From Nutrient Data (with bottle data)
- Routines have been tested with python - 3.6
- Output is EPIC Format netcdf

Help Documentation:   

```
usage: Nut_ncgen.py [-h] CruiseID btlpath nutpath output config_file_name

Merge and archive nutrient csv data and bottle data

positional arguments:
  CruiseID          provide the cruiseid
  btlpath           full path to .btl_report
  nutpath           full path to nutrient csv file
  output            full path to output folder (files will be generated there
  config_file_name  full path to config file - nut_config.yaml

optional arguments:
  -h, --help        show this help message and exit
```

Long example of usage:   
```
python Nut_ncgen.py DY1707 /Users/bell/ecoraid/2017/CTDcasts/dy1707l1/working/dy1707l1.report_btl 
 /Users/bell/ecoraid/2017/CTDcasts/dy1707l1/working/DiscreteNutrients/DY1707\ Nutrient\ Data.csv 
 /Users/bell/ecoraid/2017/CTDcasts/dy1707l1/working/ /Users/bell/Programs/Python/EcoFOCI_AtSea/config_files/nut_uml_epickeys.yaml
```

The config file is a YAML formatted file that specifies the variables and attributes of the netcdf file.  There are many examples in the config_files directory herein.


##### Bottle netcdf archive instructions
- From upcast Bottle Data
- Routines have been tested with python - 3.6

#### SCS_shptrack2gpx.py

Routine to convert GPGGA gps data to gpx files for later processing into shape files.  If data and plots for the Underway System of a noaa vessel is wanted, using SAMOS data from Florida State University is a better option. (erddap)[https://coastwatch.pfeg.noaa.gov/erddap/search/index.html?page=1&itemsPerPage=1000&searchFor=samos]

### Visualizations
#### CTD_plot.py

Various options to plot ctd profiles assuming epic style variable names.  These are some of the most commonly desired plots to look at.

usage `python CTD_plot.py {full/path/to/file.nc} -{plotflag}`

plotflag options:
```
  -h, --help            show this help message and exit
  -TSvD, --TSvD         Temperature, Salinity, SigmaT vs depth
  -OxyFluor, --OxyFluor
                        Temperature, Oxygen, Fluorometer vs depth
  -ParTurbFluor, --ParTurbFluor
                        PAR, Turbidity, Fluorometer vs depth
  -ParFluor, --ParFluor
                        PAR, Fluorometer vs depth
  -TurbFluor, --TurbFluor
                        Turbidity, Fluorometer vs depth (common for only Eco
  -ParTransFluor, --ParTransFluor
                        Transmissometer, Turbidity, Fluorometer vs depth
                        (common package for EMA)
  -TransTurbFluor, --TransTurbFluor
                        Transmissometer, Turbidity, Fluorometer vs depth
                        (common package for EMA)
  -TransFluor, --TransFluor
                        Transmissometer, Fluorometer vs depth (common package
                        for EMA)
  -has_secondary, --has_secondary
                        Flag to indicate plotting secondary values too
```

#### CruiseMap.py

Plots maps in different formats (kml,png,svg,geojson) of cruises in Pavlof database

usage `python CruiseMap.py {cruiseid} -{filetype_flag}`

################

Legal Disclaimer

This repository is a scientific product and is not official communication of the National Oceanic and Atmospheric Administration (NOAA), or the United States Department of Commerce (DOC). All NOAA GitHub project code is provided on an 'as is' basis and the user assumes responsibility for its use. Any claims against the DOC or DOC bureaus stemming from the use of this GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation, or favoring by the DOC. The DOC seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by the DOC or the United States Government.