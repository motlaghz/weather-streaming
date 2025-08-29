from ecmwf.opendata import Client
from datetime import datetime, timedelta
import requests

def download_latest_run(target_global, target_scandinavia):
    client = Client(model="aifs-single", source="ecmwf", resol="0p25")
    now = datetime.utcnow()
    date_str = now.strftime("%Y%m%d")
    date_only=now.date()
    # hours to try for latest available run, from most recent to older
    valid_hours = [18, 12, 6, 0]

    for h in valid_hours:
        origin_datetime = datetime.combine(date_only, datetime.min.time()) + timedelta(hours=h)    
        try:
            # Get the regional data for Scandinavia
            url = (
                "https://opendata.fmi.fi/download?"
                "producer=harmonie_scandinavia_surface&"
                "param=PrecipitationAmount,windums,windvms,totalcloudcover&"
                f"origintime={origin_datetime.isoformat()}Z&"
                "bbox=5,54,31,72&"
                "projection=EPSG:4326&"
                "format=grib2&"
                "timestep=360&"   # 6 hours
                "timesteps=9"     # 48 hours
            )
            
            resp = requests.get(url)
            resp.raise_for_status()

            if not resp.content:
                raise RuntimeError("No Scandinavian GRIB data returned!")
            else:
                print(f"Latest available run found: {date_str} {h:02d} UTC")
                with open(target_scandinavia, "wb") as f:
                    f.write(resp.content)
                    print("Scandinavia Saved:", target_scandinavia)
            # Get the global data
            params = {
                "type":"fc", # forecast
                "stream":"oper", # operational stream
                "step": list(range(0, 49, 6)),  # forecasts every 6h up to +48h
                "param": ["tp", "10u", "10v", "tcc"], 
                "time": h, 
                "target":target_global
            }
            client.retrieve(**params)
            print(f"Latest available run found: {date_str} {h:02d} UTC")
            print("Global Saved:", target_global)
            return date_str, h
        except Exception as e:
            # if not, try the next hour
            continue

    # if none found, try yesterday 18UTC
    yesterday = (now - timedelta(days=1)).strftime("%Y%m%d")
    return yesterday, 18