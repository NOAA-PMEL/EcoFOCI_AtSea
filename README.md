README
------
Collection of utilites for processing and visualizing common data that is gathered during field cruises.

- SCS Data
- CTD Data
- UnderWay Data   


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