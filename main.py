import time
import xarray as xr
from ecmwf_client import download_forecast
from plotting import plot_all_parameters

def run_pipeline():
    while True:
        # download and get download-time fallback
        _, download_time_globe = download_forecast("forecast_globe.grib")
        _, download_time_nordic = download_forecast("forecast_nordic.grib", area="72/-25/54/40")

        for file_name, download_time in [("forecast_nordic.grib", download_time_nordic),
                                        ("forecast_globe.grib", download_time_globe)]:
            label = file_name.split("_")[-1].split(".")[0]
            with xr.open_dataset(file_name, engine="cfgrib") as ds:
                plot_all_parameters(ds, label, time_override=download_time)

        # Wait before next update (e.g., 1 hour)
        time.sleep(3600)

if __name__ == "__main__":
    run_pipeline()