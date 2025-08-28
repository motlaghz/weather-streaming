import xarray as xr
def merge_datasets(filename):
    # Open individual datasets for each parameter and merge them
    tp = xr.open_dataset(filename, engine="cfgrib",filter_by_keys={'shortName': 'prate'})
    u10 = xr.open_dataset(filename, filter_by_keys={'shortName': '10u'})
    v10 = xr.open_dataset(filename, filter_by_keys={'shortName': '10v'})
    tcc = xr.open_dataset(filename, filter_by_keys={'shortName': 'tcc', 'typeOfLevel': 'entireAtmosphere'})

    
    tp.close()
    u10.close()
    v10.close()
    tcc.close()
    
    return tp, u10, v10, tcc
        