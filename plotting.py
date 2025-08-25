import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def plot_parameter(ds, param, label):
    time_str = str(ds[param].coords["time"].values)
    plt.figure(figsize=(10, 5))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ds[param].plot(ax=ax, cmap="Blues", transform=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.LAND, edgecolor='black', alpha=0.3)
    plt.title(f"{param} at {time_str} ({label})")
    plt.show()