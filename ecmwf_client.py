from ecmwf.opendata import Client
from datetime import datetime

def download_latest_run(target, area=None):
    client = Client(model="aifs-single", source="ecmwf", resol="0p25")
    now = datetime.utcnow()
    date_str = now.strftime("%Y%m%d")
    # hours to try for latest available run, from most recent to older
    valid_hours = [18, 12, 6, 0]

    for h in valid_hours:
        try:
            params={
                "type":"fc", # forecast
                "stream":"oper", # operational stream
                "step": 6, # 6-hour forecast
                "param":["tp", "10u", "10v", "tcc"], # precipitation, 10m u and v wind, total cloud cover
                "date":date_str, # the most recent date
                "time":h, # the hour we are trying
                "target":target # output file name
            }
            client.retrieve(**params)
            print(f"Latest available run found: {date_str} {h:02d} UTC")
            return date_str, h
        except Exception as e:
            # if not, try the next hour
            continue

    # if none found, try yesterday 18UTC
    yesterday = (now - datetime.timedelta(days=1)).strftime("%Y%m%d")
    return yesterday, 18