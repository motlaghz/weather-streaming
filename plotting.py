import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from matplotlib.widgets import RadioButtons, CheckButtons

def plot_all_parameters(ds):
    parameters = ["tp", "wind", "tcc"]
    regions = ["global", "nordic"]

    current_params = set(parameters)   # default: all selected
    current_regions = set(["global"]) # default: global only

    fig = plt.figure(figsize=(14, 10))

    # Widget axes
    ax_param = plt.axes([0.02, 0.5, 0.15, 0.35])
    check_param = CheckButtons(ax_param, parameters, [True, True, True])

    ax_region = plt.axes([0.02, 0.25, 0.15, 0.2])
    check_region = CheckButtons(ax_region, regions, [True, False])

    plot_axes = []
    colorbars = []

    def plot_map(selected_params, selected_regions):
        nonlocal plot_axes, colorbars
        # remove old axes and colorbars
        for ax in plot_axes:
            fig.delaxes(ax)
        for cbar in colorbars:
            cbar.remove()
        plot_axes, colorbars = [], []

        time_str = str(ds["tp"].coords["valid_time"].values)[:19]

        # if nothing selected, nothing to draw
        if not selected_params or not selected_regions:
            fig.canvas.draw_idle()
            return

        # grid for plots
        nrows = len(selected_params)
        ncols = len(selected_regions)
        gs = fig.add_gridspec(nrows, ncols, left=0.25, right=0.95, 
                              top=0.95, bottom=0.1, hspace=0.25, wspace=0.25)

        for i, p in enumerate(selected_params):
            for j, region in enumerate(selected_regions):
                ax = fig.add_subplot(gs[i, j], projection=ccrs.PlateCarree())
                plot_axes.append(ax)

                # region extent
                if region.lower() == "nordic":
                    extent = [5, 32, 55, 72]
                else:
                    extent = [ds.longitude.min().item(), ds.longitude.max().item(),
                              ds.latitude.min().item(), ds.latitude.max().item()]

                lon_min, lon_max, lat_min, lat_max = extent
                if ds.latitude[0] > ds.latitude[-1]:
                    ds_sel = ds.sel(latitude=slice(lat_max, lat_min), longitude=slice(lon_min, lon_max))
                else:
                    ds_sel = ds.sel(latitude=slice(lat_min, lat_max), longitude=slice(lon_min, lon_max))

                ax.set_extent(extent, crs=ccrs.PlateCarree())
                ax.add_feature(cfeature.COASTLINE)
                ax.add_feature(cfeature.BORDERS)

                # plot per parameter
                if p == "tp":
                    im = ds_sel["tp"].plot(ax=ax, cmap="Blues", transform=ccrs.PlateCarree(),
                                           add_colorbar=False)
                    cbar = fig.colorbar(im, ax=ax, orientation="vertical", pad=0.02)
                    cbar.set_label("Total Precipitation (m)")
                    colorbars.append(cbar)
                    ax.set_title(f"Precipitation at {time_str} ({region})")

                elif p == "wind":
                    skip = (slice(None, None, 3), slice(None, None, 3)) if region.lower()=="nordic" else (slice(None, None, 10), slice(None, None, 10))
                    lats = ds_sel["latitude"].values[skip[0]]
                    lons = ds_sel["longitude"].values[skip[1]]
                    u = ds_sel["u10"].values[skip]
                    v = ds_sel["v10"].values[skip]
                    Lon, Lat = np.meshgrid(lons, lats)
                    wind_speed = np.sqrt(u**2 + v**2)
                    scale = 700 if region=="global" else 150
                    q = ax.quiver(Lon, Lat, u, v, wind_speed, cmap="coolwarm",
                                  transform=ccrs.PlateCarree(), scale=scale)
                    cbar = fig.colorbar(q, ax=ax, orientation="vertical", pad=0.02)
                    cbar.set_label("Wind speed (m/s)")
                    colorbars.append(cbar)
                    ax.set_title(f"Wind at {time_str} ({region})")

                elif p == "tcc":
                    im = ds_sel["tcc"].plot(ax=ax, cmap="bone", transform=ccrs.PlateCarree(),
                                            add_colorbar=False)
                    cbar = fig.colorbar(im, ax=ax, orientation="vertical", pad=0.02)
                    cbar.set_label("Total Cloud Cover (fraction)")
                    colorbars.append(cbar)
                    ax.set_title(f"Cloud Cover at {time_str} ({region})")

        fig.canvas.draw_idle()

    # update callbacks
    def update_param(label):
        if label in current_params:
            current_params.remove(label)
        else:
            current_params.add(label)
        plot_map(list(current_params), list(current_regions))

    def update_region(label):
        if label in current_regions:
            current_regions.remove(label)
        else:
            current_regions.add(label)
        plot_map(list(current_params), list(current_regions))

    check_param.on_clicked(update_param)
    check_region.on_clicked(update_region)

    # initial draw
    plot_map(list(current_params), list(current_regions))

    plt.show()
