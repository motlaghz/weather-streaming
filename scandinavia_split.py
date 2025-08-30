"""
Module for splitting weather datasets from GRIB files into separate parameter datasets.
"""

import logging
from typing import Tuple
import xarray as xr


def split_datasets(
    filename: str,
) -> Tuple[xr.Dataset, xr.Dataset, xr.Dataset, xr.Dataset]:
    """
    Split a GRIB file into separate datasets for each weather parameter.

    Args:
        filename (str): Path to the GRIB file to split.

    Returns:
        Tuple[xr.Dataset, xr.Dataset, xr.Dataset, xr.Dataset]:
            Tuple containing datasets for precipitation, u-wind, v-wind, and total cloud cover.
    """
    logging.basicConfig(level=logging.INFO)

    try:
        # Common backend kwargs to avoid index path issues
        backend_kwargs = {"indexpath": ""}

        # Open individual datasets for each parameter
        precipitation = xr.open_dataset(
            filename,
            engine="cfgrib",
            decode_timedelta=True,
            filter_by_keys={"shortName": "rain_con"},
            backend_kwargs=backend_kwargs,
        )

        u_wind_10m = xr.open_dataset(
            filename,
            engine="cfgrib",
            decode_timedelta=True,
            filter_by_keys={"shortName": "10u"},
            backend_kwargs=backend_kwargs,
        )

        v_wind_10m = xr.open_dataset(
            filename,
            engine="cfgrib",
            decode_timedelta=True,
            filter_by_keys={"shortName": "10v"},
            backend_kwargs=backend_kwargs,
        )

        total_cloud_cover = xr.open_dataset(
            filename,
            engine="cfgrib",
            decode_timedelta=True,
            filter_by_keys={"shortName": "tcc", "typeOfLevel": "entireAtmosphere"},
            backend_kwargs=backend_kwargs,
        )

        logging.info(f"Successfully split datasets from {filename}")

        # Close the datasets to free up resources
        precipitation.close()
        u_wind_10m.close()
        v_wind_10m.close()
        total_cloud_cover.close()

        return precipitation, u_wind_10m, v_wind_10m, total_cloud_cover

    except Exception as exc:
        logging.error(f"Failed to split datasets from {filename}: {exc}")
        raise
