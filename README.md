# Weather Streaming & Visualization Pipeline

## Description
This project provides an interactive pipeline for downloading, processing, and visualising short-range weather forecasts from ECMWF Open Data (global forecasts) and the Finnish Meteorological Institute (FMI) (regional forecasts for Scandinavia).  

It produces interactive maps with checkboxes and sliders that let you explore precipitation, wind, and cloud cover across global and Scandinavian domains.  

---

## Features  

- **Automated data ingestion**  
  - Downloads the latest available ECMWF global forecast (AIFS model, 0.25° resolution).  
  - Downloads FMI HARMONIE-AROME forecasts for Scandinavia (regional 2.5 km).  

- **Two coverage domains**  
  - Global (ECMWF)  
  - Scandinavia (FMI regional model, bbox = 5–31°E, 54–72°N)  

- **Interactive plotting**  
  - Parameters: Total precipitation, surface winds, cloud cover.  
  - Regions: Global vs. Scandinavia.  
  - Time slider for forecast steps (+0h to +48h, every 6 hours).  

- **Visualisation tools**  
  - Precipitation plotted as colour maps.  
  - Winds plotted as vector fields (quivers).  
  - Cloud cover plotted as shaded fields.  

---

## Setup
Create a conda environment to install the required libraries:
```bash
conda create -n myenv
conda activate myenv
```
Install dependencies found in requirements.txt:
```bash
pip install -r requirements.txt
```
To run this visualization Python 3.9+ is needed.
Dependencies include:
```ecmwf-opendata``` – ECMWF Open Data API client
```requests``` – for FMI downloads
```xarray + cfgrib + eccodes``` – GRIB file reading
```matplotlib + cartopy``` – interactive map plotting

## Notes
Grib forecast files are ignored by ```.gitignore``` (they can be several GB).
## Usage
Run the pipeline:
```bash
python main.py
```
The script will:
 - Download the latest forecasts.
 - Open an interactive map window with parameter/region checkboxes and a time slider.
 - Wait for one hour, then re-download and update.

## Example Screenshot
