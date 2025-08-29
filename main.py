import time
import xarray as xr
from client import download_latest_run
from plotting import plot_all_parameters
from scandinavia_merge import merge_datasets

def run_pipeline():
    while True:
        # Download forecasts
        _ , _ = download_latest_run("forecast_globe.grib","forecast_scandinavia.grib")
        file_name_global = "forecast_globe.grib" 

        tp, u10, v10, tcc = merge_datasets("forecast_scandinavia.grib")
        
        with xr.open_dataset(file_name_global, engine="cfgrib") as ds1, xr.merge([tp, u10, v10, tcc],compat="override") as ds2:
            plot_all_parameters(ds1, ds2)
            # print(ds1.coords['time'].values)
            # print(ds2.coords['time'].values)

        # Wait before next update (e.g., 1 hour)
        time.sleep(3600)

if __name__ == "__main__":
    run_pipeline()