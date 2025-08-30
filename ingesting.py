"""
Module for downloading the latest weather forecast data for global and Scandinavian regions.
"""

import logging
from datetime import datetime, timedelta, timezone
import requests
from ecmwf.opendata import Client
from typing import Optional

def download_latest_run(
    target_global: str, 
    target_scandinavia: str,
    last_date_str: Optional[str] = None,
    last_hour: Optional[int] = None,
) -> tuple[str, int, bool]:
    """
    Download the latest available weather forecast data for global and Scandinavian regions.

    Args:
        target_global (str): Path to save the global forecast GRIB file.
        target_scandinavia (str): Path to save the Scandinavian forecast GRIB file.
        last_date_str (str, optional): Previously downloaded date string (YYYYMMDD).
        last_hour (int, optional): Previously downloaded hour (UTC).

    Returns:
        tuple[str, int, bool]: The date string, hour, and a flag indicating if new data was downloaded.
    """
    logging.basicConfig(level=logging.INFO)
    client = Client(model="aifs-single", source="ecmwf", resol="0p25")
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y%m%d")
    date_only = now.date()
    valid_hours = [18, 12, 6, 0]  # Try these hours for the latest available run

    for hour in valid_hours:
        origin_datetime = datetime.combine(date_only, datetime.min.time()) + timedelta(
            hours=hour
        )

        # Skip if this run was already downloaded (but only if it's not the first time)
        if last_date_str is not None and last_hour is not None:
            if (date_str, hour) == (last_date_str, last_hour):
                logging.info(
                    f"No new run available ({date_str} {hour:02d} UTC). Skipping download."
                )
                return date_str, hour, False
        try:
            # Download Scandinavian regional data
            url = (
                "https://opendata.fmi.fi/download?"
                "producer=harmonie_scandinavia_surface&"
                "param=PrecipitationAmount,windums,windvms,totalcloudcover&"
                f"origintime={origin_datetime.isoformat()}Z&"
                "bbox=5,54,31,72&"
                "projection=EPSG:4326&"
                "format=grib2&"
                "timestep=360&"  # 6 hours
                "timesteps=9"  # 48 hours
            )
            response = requests.get(url)

            if not response.content:
                raise RuntimeError("No Scandinavian GRIB data returned!")

            with open(target_scandinavia, "wb") as f:
                f.write(response.content)
            logging.info(f"Latest available for FMI run found: {date_str} {hour:02d} UTC")
            logging.info(f"Scandinavian data saved: {target_scandinavia}")

            # Download global data
            params = {
                "type": "fc",  # forecast
                "stream": "oper",  # operational stream
                "step": list(range(0, 49, 6)),  # forecasts every 6h up to +48h
                "param": ["tp", "10u", "10v", "tcc"],
                "time": hour,
                "target": target_global,
            }
            client.retrieve(**params)
            logging.info(f"Latest available for ECMWF run found: {date_str} {hour:02d} UTC")
            logging.info(f"Global data saved: {target_global}")
            return date_str, hour, True
        except Exception as exc:
            logging.warning(f"Run {date_str} {hour:02d} UTC not available: {exc}")
            continue

    # If none found, try yesterday 18UTC
    yesterday = (now - timedelta(days=1)).strftime("%Y%m%d")
    logging.warning(
        "No available runs found for today. Falling back to yesterday 18 UTC."
    )
    if (yesterday, 18) == (last_date_str, last_hour):
        logging.info(f"No new run available ({yesterday} 18 UTC). Skipping download.")
        return yesterday, 18, False
    return yesterday, 18, True
