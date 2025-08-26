import time
import xarray as xr
from ecmwf_client import download_latest_run
from plotting import plot_all_parameters

def run_pipeline():
    while True:
        # Download global forecasts
        _ , _ = download_latest_run("forecast_globe.grib")
        
        file_name = "forecast_globe.grib" 
        with xr.open_dataset(file_name, engine="cfgrib") as ds:
            plot_all_parameters(ds, "global", region="global")
            plot_all_parameters(ds, "nordic", region="nordic")

        # Wait before next update (e.g., 1 hour)
        time.sleep(3600)

if __name__ == "__main__":
    run_pipeline()