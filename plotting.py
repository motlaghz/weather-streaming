import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from matplotlib.widgets import CheckButtons, Slider

# -------------------------------
# Helper functions
# -------------------------------

def setup_widgets(fig, n_steps,ds):
    """Create parameter, region checkboxes and time slider widgets."""
    ax_param = plt.axes([0.02, 0.5, 0.15, 0.35])
    check_param = CheckButtons(ax_param, ["tp", "wind", "tcc"], [True, False, False])

    ax_region = plt.axes([0.02, 0.25, 0.15, 0.2])
    check_region = CheckButtons(ax_region, ["global", "nordic"], [False, True])

    ax_slider = plt.axes([0.25, 0.03, 0.65, 0.03])
    slider = Slider(ax_slider, "Time step", 0, n_steps - 1, valinit=0, valstep=1)

    # create separate axes for tick labels
    ax_ticks = plt.axes([0.25, 0.03, 0.65, 0.03], frameon=False)
    ax_ticks.set_xlim(0, n_steps-1)
    ax_ticks.set_xticks(range(0, n_steps, max(1, n_steps//10)))
    ax_ticks.set_xticklabels([f"{int(s)}h" for s in ds["step"].values/3600000000000])
    ax_ticks.get_yaxis().set_ticks([])
    return check_param, check_region, slider

def update_params(current_params, label):
    """Toggle selected parameter."""
    if label in current_params:
        current_params.remove(label)
    else:
        current_params.add(label)

def update_regions(current_regions, label):
    """Toggle selected region."""
    if label in current_regions:
        current_regions.remove(label)
    else:
        current_regions.add(label)

# -------------------------------
# Main plotting logic
# -------------------------------

def plot_map(fig, ds, selected_params, selected_regions, time_index, plot_axes, colorbars):
    """Draw the selected parameters and regions at the specified time step."""
    # remove only previous plotting axes
    for ax in plot_axes:
        fig.delaxes(ax)
    for cbar in colorbars:
        cbar.remove()

    plot_axes = []
    colorbars_new = []

    ds_t = ds.isel(step=time_index)
    time_str = str(ds_t["tp"].coords["valid_time"].values)[:19].replace("T", ", ")

    if not selected_params or not selected_regions:
        fig.canvas.draw_idle()
        return plot_axes, colorbars

    # grid layout
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
                ds_sel = ds_t.sel(latitude=slice(lat_max, lat_min),
                                  longitude=slice(lon_min, lon_max))
            else:
                ds_sel = ds_t.sel(latitude=slice(lat_min, lat_max),
                                  longitude=slice(lon_min, lon_max))

            ax.set_extent(extent, crs=ccrs.PlateCarree())
            ax.add_feature(cfeature.COASTLINE)
            ax.add_feature(cfeature.BORDERS)

            # --- plotting each parameter ---
            if p == "tp":
                im = ds_sel["tp"].plot(ax=ax, cmap="Blues", transform=ccrs.PlateCarree(),
                                       add_colorbar=False)
                cbar = fig.colorbar(im, ax=ax, orientation="vertical", pad=0.02)
                cbar.set_label("Total Precipitation (m)")
                colorbars_new.append(cbar)
                ax.set_title(f"Precipitation at {time_str} ({region})")

            elif p == "wind":
                skip = (slice(None, None, 3), slice(None, None, 3)) if region.lower() == "nordic" else (slice(None, None, 10), slice(None, None, 10))
                lats = ds_sel["latitude"].values[skip[0]]
                lons = ds_sel["longitude"].values[skip[1]]
                u = ds_sel["u10"].values[skip]
                v = ds_sel["v10"].values[skip]
                Lon, Lat = np.meshgrid(lons, lats)
                wind_speed = np.sqrt(u**2 + v**2)
                scale = 700 if region == "global" else 150
                q = ax.quiver(Lon, Lat, u, v, wind_speed, cmap="coolwarm",
                              transform=ccrs.PlateCarree(), scale=scale)
                cbar = fig.colorbar(q, ax=ax, orientation="vertical", pad=0.02)
                cbar.set_label("Wind speed (m/s)")
                colorbars_new.append(cbar)
                ax.set_title(f"Wind at {time_str} ({region})")

            elif p == "tcc":
                im = ds_sel["tcc"].plot(ax=ax, cmap="bone", transform=ccrs.PlateCarree(),
                                        add_colorbar=False)
                cbar = fig.colorbar(im, ax=ax, orientation="vertical", pad=0.02)
                cbar.set_label("Total Cloud Cover (fraction)")
                colorbars_new.append(cbar)
                ax.set_title(f"Cloud Cover at {time_str} ({region})")

    fig.canvas.draw_idle()
    return plot_axes, colorbars_new

# -------------------------------
# Entry point function
# -------------------------------

def plot_all_parameters(ds):
    """Main function to display interactive weather maps with widgets."""
    current_params = set(["tp"])
    current_regions = set(["nordic"])
    current_step = 0

    n_steps = len(ds["step"])
    fig = plt.figure(figsize=(14, 10))

    # create widgets
    check_param, check_region, step_slider = setup_widgets(fig, n_steps,ds)
    widget_axes = [check_param.ax, check_region.ax, step_slider.ax]

    plot_axes = []  # list to track plotting axes
    colorbars = []  # list to track colorbars
    # connect callbacks
    def on_param_change(label):
        update_params(current_params, label)
        nonlocal plot_axes, colorbars
        plot_axes, colorbars = plot_map(fig, ds, current_params, current_regions, int(step_slider.val), plot_axes, colorbars)

    def on_region_change(label):
        update_regions(current_regions, label)
        nonlocal plot_axes, colorbars
        plot_axes, colorbars = plot_map(fig, ds, current_params, current_regions, int(step_slider.val), plot_axes, colorbars)

    def on_slider_change(val):
        nonlocal plot_axes, colorbars
        plot_axes, colorbars = plot_map(fig, ds, current_params, current_regions, int(val), plot_axes, colorbars)

    check_param.on_clicked(on_param_change)
    check_region.on_clicked(on_region_change)
    step_slider.on_changed(on_slider_change)

    # initial draw
    plot_axes, colorbars = plot_map(fig, ds, current_params, current_regions, current_step, plot_axes, colorbars)

    plt.show()
