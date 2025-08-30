import xarray as xr
def split_datasets(filename):
    # Open individual datasets for each parameter and merge them
    tp = xr.open_dataset(filename, engine="cfgrib",filter_by_keys={'shortName': 'rain_con'}, backend_kwargs={"indexpath": ""})
    u10 = xr.open_dataset(filename, filter_by_keys={'shortName': '10u'}, backend_kwargs={"indexpath": ""})
    v10 = xr.open_dataset(filename, filter_by_keys={'shortName': '10v'}, backend_kwargs={"indexpath": ""})
    tcc = xr.open_dataset(filename, filter_by_keys={'shortName': 'tcc', 'typeOfLevel': 'entireAtmosphere'}, backend_kwargs={"indexpath": ""})

    
    tp.close()
    u10.close()
    v10.close()
    tcc.close()
    
    return tp, u10, v10, tcc
        