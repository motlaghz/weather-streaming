import time
import xarray as xr
from ingesting import download_latest_run
from plotting import plot_all_parameters
from scandinavia_split import split_datasets


def run_pipeline():
    while True:
        # Download forecasts
        _ , _ = download_latest_run("forecast_global.grib","forecast_scandinavia.grib")
        file_name_global = "forecast_global.grib" 

        tp, u10, v10, tcc = split_datasets("forecast_scandinavia.grib")
        
        with xr.open_dataset(file_name_global, engine="cfgrib", backend_kwargs={"indexpath": ""}) as ds1, xr.merge([tp, u10, v10, tcc],compat="override") as ds2:
            plot_all_parameters(ds1, ds2)

        # Wait before next update (e.g., 1 hour)
        time.sleep(3600)

if __name__ == "__main__":
    run_pipeline()