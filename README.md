README
------
Collection of utilites for processing and visualizing common data that is gathered during field cruises.

- SCS Data
- CTD Data
- UnderWay Data   

#### EPIC/CF netcdf generation
**TODO:**
- From discrete Oxygen/Salinity Calibration/Characterization measurements

##### Nutrient netcdf archive instructions
- From Nutrient Data (with bottle data)

##### Bottle netcdf archive instructions
- From upcast Bottle Data

#### SCS_shptrack2gpx.py

Routine to convert GPGGA gps data to gpx files for later processing into shape files.

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


################

Legal Disclaimer

This repository is a scientific product and is not official communication of the National Oceanic and Atmospheric Administration (NOAA), or the United States Department of Commerce (DOC). All NOAA GitHub project code is provided on an 'as is' basis and the user assumes responsibility for its use. Any claims against the DOC or DOC bureaus stemming from the use of this GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation, or favoring by the DOC. The DOC seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by the DOC or the United States Government.