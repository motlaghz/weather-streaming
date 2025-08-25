from ecmwf.opendata import Client
from datetime import datetime

def download_forecast(target, area=None):
    client = Client(model="aifs-single", source="ecmwf", resol="0p25")
    params = {
        "stream": "oper", # operational data
        "type": "fc", # forecast
        "step": 6, # 6-hour forecast
        "date": -1, # latest available
        "param": "tp/10u/10v/tcc", # total precipitation, 10m U and V wind, total cloud cover
        "target": target # path to save the file
    }
    if area:
        params["area"] = area
    client.retrieve(**params)
    # return an ISO timestamp for use in titles if GRIB time missing
    ts = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    print(f"Forecast saved to {target} (downloaded {ts})")
    return target, ts