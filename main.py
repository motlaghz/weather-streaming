"""
Main pipeline for weather data streaming and visualization.

This module orchestrates the download, processing, and visualization of weather forecast data
for both global and Scandinavian regions.
"""

import logging
import time
import xarray as xr
from ingesting import download_latest_run
from plotting import plot_all_parameters
from scandinavia_split import split_datasets

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
GLOBAL_FORECAST_FILE = "forecast_global.grib"
SCANDINAVIA_FORECAST_FILE = "forecast_scandinavia.grib"
UPDATE_INTERVAL_SECONDS = 3600  # 1 hour


def run_pipeline() -> None:
    """
    Run the main weather data pipeline.

    Downloads the latest weather forecasts, processes the data, and displays
    interactive visualizations. Runs continuously with periodic updates.
    """
    logging.info("Starting weather data pipeline...")
    last_date_str, last_hour = None, None # Track last processed run
    try:
        while True:
            logging.info("Starting new pipeline iteration...")

            # Download latest forecast data
            date_str, hour, new_data = download_latest_run(
                GLOBAL_FORECAST_FILE, SCANDINAVIA_FORECAST_FILE, last_date_str, last_hour
            )

            if not new_data:
                logging.info("No new forecast data. Skipping processing.")
            else:
                logging.info(f"Processing forecasts for {date_str} {hour:02d} UTC")

                # Process Scandinavian data
                precipitation, u_wind, v_wind, cloud_cover = split_datasets(
                    SCANDINAVIA_FORECAST_FILE
                )
                logging.info("Split Scandinavian datasets successfully")

                # Open datasets and create visualization
                try:
                    with xr.open_dataset(
                        GLOBAL_FORECAST_FILE,
                        engine="cfgrib",
                        decode_timedelta=True,
                        backend_kwargs={"indexpath": ""},
                    ) as global_dataset, xr.merge(
                        [precipitation, u_wind, v_wind, cloud_cover], compat="override"
                    ) as scandinavian_dataset:

                        logging.info("Creating interactive weather visualization...")
                        plot_all_parameters(global_dataset, scandinavian_dataset)
                        # Update last processed run
                        last_date_str, last_hour = date_str, hour
                except Exception as exc:
                    logging.error(f"Failed to process datasets: {exc}")
                    continue

            logging.info(
                f"Waiting {UPDATE_INTERVAL_SECONDS // 60} minutes before next update..."
            )
            time.sleep(UPDATE_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        logging.info("Pipeline stopped gracefully by user.")
    except Exception as exc:
        logging.error(f"Pipeline failed with error: {exc}")
        raise


if __name__ == "__main__":
    run_pipeline()
