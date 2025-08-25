import time
import xarray as xr
from ecmwf_client import download_forecast
from plotting import plot_all_parameters

def run_pipeline():
    while True:
        # Download global and regional forecasts
        download_forecast("forecast_globe.grib")
        download_forecast("forecast_nordic.grib", area="72/-25/54/40")

        for file_name in ["forecast_nordic.grib", "forecast_globe.grib"]:
            label = file_name.split("_")[-1].split(".")[0]  # gets 'nordic' or 'globe'
            with xr.open_dataset(file_name, engine="cfgrib") as ds:
                plot_all_parameters(ds, label)

        # Wait before next update (e.g., 1 hour)
        time.sleep(3600)

if __name__ == "__main__":
    run_pipeline()