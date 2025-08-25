import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np

def plot_all_parameters(ds, label):
    time_str = str(ds["tp"].coords["time"].values)
    fig, axes = plt.subplots(3, 1, figsize=(8, 18), subplot_kw={'projection': ccrs.PlateCarree()})

    # Precipitation
    ax = axes[0]
    im = ds["tp"].plot(ax=ax, cmap="Blues", transform=ccrs.PlateCarree(), 
        cbar_kwargs={
        "label": "Total Precipitation (m)",
        "shrink": 0.5,
        "pad": 0.02,
        "orientation": "vertical",
        })
    ax.set_title(f"Precipitation at {time_str} ({label})")
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.LAND, edgecolor='black', alpha=0.3)
    # cbar = plt.colorbar(im, ax=ax, orientation="vertical", fraction=0.03, pad=0.02)
    # cbar.ax.set_aspect(0.2)

    # Wind (arrows colored by speed)
    ax = axes[1]
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.LAND, edgecolor='black', alpha=0.3)
    ax.set_title(f"Wind at {time_str} ({label})")
    skip = (slice(None, None, 10), slice(None, None, 10))
    lats = ds["latitude"].values[skip[0]]
    lons = ds["longitude"].values[skip[1]]
    u = ds["u10"].values[skip]
    v = ds["v10"].values[skip]
    Lon, Lat = np.meshgrid(lons, lats)
    wind_speed = np.sqrt(u**2 + v**2)
    q = ax.quiver(Lon, Lat, u, v, wind_speed, cmap="coolwarm", transform=ccrs.PlateCarree(), scale=700)
    cbar = plt.colorbar(q, ax=ax, orientation="vertical", shrink=0.5,pad=0.02)
    # cbar.ax.set_aspect(30)
    cbar.set_label("Wind speed (m/s)")

    # Cloud cover
    ax = axes[2]
    im = ds["tcc"].plot(ax=ax, cmap="bone", transform=ccrs.PlateCarree(),  
        cbar_kwargs={
        "label": "Total Cloud Cover (fraction)",
        "shrink": 0.5,
        "pad": 0.02,
        "orientation": "vertical",
        })
    ax.set_title(f"Cloud Cover at {time_str} ({label})")
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.LAND, edgecolor='black', alpha=0.3)
    # cbar = plt.colorbar(im, ax=ax, orientation="vertical", fraction=0.03, pad=0.02)
    # cbar.ax.set_aspect(0.2)

    plt.tight_layout()
    plt.show()