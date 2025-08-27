import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from matplotlib.widgets import CheckButtons, Slider

def plot_all_parameters(ds):
    parameters = ["tp", "wind", "tcc"]
    regions = ["global", "nordic"]

    current_params = set(["tp"])   # default: all selected
    current_regions = set(["nordic"]) # default: global only
    current_step = 0                   # start with first step

    steps = ds["step"].values
    valid_times = ds["valid_time"].values if "valid_time" in ds else ds["time"].values + ds["step"].values

    fig = plt.figure(figsize=(14, 10))

    # Widget axes
    ax_param = plt.axes([0.02, 0.5, 0.15, 0.35])
    check_param = CheckButtons(ax_param, parameters, [True, False, False]) # default selections

    ax_region = plt.axes([0.02, 0.25, 0.15, 0.2])
    check_region = CheckButtons(ax_region, regions, [False, True]) # default selections

    # Slider axis
    ax_slider = plt.axes([0.25, 0.03, 0.65, 0.03])
    step_slider = Slider(ax_slider, "Forecast step", 0, len(steps) - 1, valinit=current_step, valstep=1)

    plot_axes = []
    colorbars = []

    def plot_map(selected_params, selected_regions, step_idx=current_step):
        nonlocal plot_axes, colorbars
        # remove old axes and colorbars
        for ax in plot_axes:
            fig.delaxes(ax)
        for cbar in colorbars:
            cbar.remove()
        plot_axes, colorbars = [], []

        time_str = str(valid_times[step_idx])[:19]

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
                    im = ds_sel["tp"].isel(step=step_idx).plot(
                        ax=ax, cmap="Blues", transform=ccrs.PlateCarree(),
                        add_colorbar=False
                    )
                    cbar = fig.colorbar(im, ax=ax, orientation="vertical", pad=0.02)
                    cbar.set_label("Total Precipitation (m)")
                    colorbars.append(cbar)
                    ax.set_title(f"Precipitation at {time_str} ({region})")

                elif p == "wind":
                    skip = (slice(None, None, 3), slice(None, None, 3)) if region.lower()=="nordic" else (slice(None, None, 10), slice(None, None, 10))
                    lats = ds_sel["latitude"].values[skip[0]]
                    lons = ds_sel["longitude"].values[skip[1]]
                    u = ds_sel["u10"].isel(step=step_idx).values[skip]
                    v = ds_sel["v10"].isel(step=step_idx).values[skip]
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
                    im = ds_sel["tcc"].isel(step=step_idx).plot(
                        ax=ax, cmap="bone", transform=ccrs.PlateCarree(),
                        add_colorbar=False
                    )
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
        plot_map(list(current_params), list(current_regions), int(step_slider.val))

    def update_region(label):
        if label in current_regions:
            current_regions.remove(label)
        else:
            current_regions.add(label)
        plot_map(list(current_params), list(current_regions), int(step_slider.val))

    def update_step(val):
        plot_map(list(current_params), list(current_regions), int(val))

    check_param.on_clicked(update_param)
    check_region.on_clicked(update_region)
    step_slider.on_changed(update_step)

    # initial draw
    plot_map(list(current_params), list(current_regions), current_step)

    plt.show()
