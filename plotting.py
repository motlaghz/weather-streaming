import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from matplotlib.widgets import CheckButtons, Slider
from matplotlib.gridspec import GridSpec

# -------------------------------
# Helper functions
# -------------------------------

def setup_widgets(fig, n_steps, ds):
    """Create parameter, region checkboxes and time slider widgets."""
    # full display names
    param_vars = ["Total Precipitation", "Surface Wind", "Total Cloud Cover"]
    region_vars = ["Global", "Scandinavia"]

    # Parameter checkbuttons
    ax_param = plt.axes([0.02, 0.5, 0.15, 0.35])
    fig.text(0.02 + 0.075, 0.82, "Parameters", ha="center", va="bottom", fontsize=12, fontweight="bold")
    check_param = CheckButtons(ax_param, param_vars, [True, False, False])

    # Region checkbuttons
    ax_region = plt.axes([0.02, 0.25, 0.15, 0.2])
    fig.text(0.02 + 0.075, 0.42, "Coverage", ha="center", va="bottom", fontsize=12, fontweight="bold")
    check_region = CheckButtons(ax_region, region_vars, [False, True])

    # Time slider
    ax_slider = plt.axes([0.25, 0.03, 0.65, 0.03])
    slider = Slider(ax_slider, "Time step", 0, n_steps - 1, valinit=0, valstep=1)

    # Tick labels
    ax_ticks = plt.axes([0.25, 0.03, 0.65, 0.03], frameon=False)
    ax_ticks.set_xlim(0, n_steps-1)
    ax_ticks.set_xticks(range(0, n_steps, max(1, n_steps//10)))
    ax_ticks.set_xticklabels([f"{int(s)}h" for s in ds["step"].values/3600000000000])
    ax_ticks.get_yaxis().set_ticks([])

    return check_param, param_vars, check_region, region_vars, slider

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

def plot_map(fig, ds1, ds2, selected_params, selected_regions, time_index,
             plot_axes, colorbars, suptitle):
    """Draw the selected parameters and regions at the specified time step."""
    
    # remove previous plotting axes and colorbars
    for ax in plot_axes:
        fig.delaxes(ax)
    for cbar in colorbars:
        cbar.remove()
    
    plot_axes = []
    colorbars_new = []

    # get valid time string from global dataset
    ds_t_global = ds1.isel(step=time_index)
    time_str = str(ds_t_global["tp"].coords["valid_time"].values)[:19].replace("T", ", ")
    
    # update suptitle (slightly higher)
    suptitle.set_y(0.99)
    suptitle.set_x(0.6)
    suptitle.set_text(f"Valid time: {time_str}")

    if not selected_params or not selected_regions:
        fig.canvas.draw_idle()
        return plot_axes, colorbars_new

    # grid layout
    nrows = len(selected_params)
    ncols = len(selected_regions)
    widths = [1.5 if r == "Global" else 1 for r in selected_regions]
    gs = fig.add_gridspec(nrows, ncols, left=0.25, right=0.95,
                          top=0.95, bottom=0.1, hspace=0.25, wspace=0.25,
                          width_ratios=widths)

    # loop over parameters and regions
    for i, p in enumerate(selected_params):
        for j, region in enumerate(selected_regions):
            ax = fig.add_subplot(gs[i, j], projection=ccrs.PlateCarree())
            plot_axes.append(ax)

            # select dataset and extent
            if region == "Scandinavia":
                ds = ds2
                extent = [5, 31, 54, 72]
                tp_var = "rain_con"
            else:  # Global
                ds = ds1
                extent = [ds.longitude.min().item(), ds.longitude.max().item(),
                          ds.latitude.min().item(), ds.latitude.max().item()]
                tp_var = "tp"

            ds_t = ds.isel(step=time_index)
            ax.set_extent(extent, crs=ccrs.PlateCarree())
            ax.add_feature(cfeature.COASTLINE)
            ax.add_feature(cfeature.BORDERS)

            # --- plotting each parameter ---
            if p == "Total Precipitation":
                im = ds_t[tp_var].plot(ax=ax, cmap="Blues", transform=ccrs.PlateCarree(),
                                       add_colorbar=False, vmin=0, vmax=50)
                cbar = fig.colorbar(im, ax=ax, orientation="vertical", pad=0.02, 
                                    fraction=0.04 if region == "Scandinavia" else 0.025)
                cbar.set_label("Total Precipitation (m)")
                colorbars_new.append(cbar)
                ax.set_title(f"Total Precipitation ({region})")

            elif p == "Surface Wind":
                skip = (slice(None, None, 10), slice(None, None, 10))
                lats = ds_t["latitude"].values[skip[0]]
                lons = ds_t["longitude"].values[skip[1]]
                u = ds_t["u10"].values[skip]
                v = ds_t["v10"].values[skip]
                Lon, Lat = np.meshgrid(lons, lats)
                wind_speed = np.sqrt(u**2 + v**2)
                scale = 700 if region == "Global" else 150
                vmin, vmax = 0, 40
                q = ax.quiver(Lon, Lat, u, v, wind_speed, cmap="coolwarm",
                              transform=ccrs.PlateCarree(), scale=scale,
                              clim=(vmin, vmax))
                cbar = fig.colorbar(q, ax=ax, orientation="vertical", pad=0.02,
                                    fraction=0.04 if region == "Scandinavia" else 0.025)
                cbar.set_label("Wind speed (m/s)")
                colorbars_new.append(cbar)
                ax.set_title(f"Surface Wind ({region})")

            elif p == "Total Cloud Cover":
                im = ds_t["tcc"].plot(ax=ax, cmap="bone", transform=ccrs.PlateCarree(),
                                      add_colorbar=False, vmin=0, vmax=100)
                cbar = fig.colorbar(im, ax=ax, orientation="vertical", pad=0.02,
                                    fraction=0.04 if region == "Scandinavia" else 0.025)
                cbar.set_label("Total Cloud Cover (fraction)")
                colorbars_new.append(cbar)
                ax.set_title(f"Total Cloud Cover ({region})")

    fig.canvas.draw_idle()
    return plot_axes, colorbars_new


# -------------------------------
# Entry point function
# -------------------------------

def plot_all_parameters(ds1, ds2):
    """Main function to display interactive weather maps with widgets."""
    current_params = set(["Total Precipitation"])
    current_regions = set(["Scandinavia"])
    current_step = 0
    
    n_steps = len(ds1["step"])
    fig = plt.figure(figsize=(14, 10))

    # create suptitle (updated every redraw)
    suptitle = fig.suptitle("", fontsize=16)

    # create widgets
    check_param, param_vars, check_region, region_vars, step_slider = setup_widgets(fig, n_steps, ds1)
    widget_axes = [check_param.ax, check_region.ax, step_slider.ax]

    plot_axes = []  # list to track plotting axes
    colorbars = []  # list to track colorbars

    # connect callbacks
    def on_param_change(label):
        update_params(current_params, label)
        nonlocal plot_axes, colorbars
        plot_axes, colorbars = plot_map(fig, ds1, ds2, current_params, current_regions,
                                        int(step_slider.val), plot_axes, colorbars,
                                        suptitle)

    def on_region_change(label):
        update_regions(current_regions, label)
        nonlocal plot_axes, colorbars
        plot_axes, colorbars = plot_map(fig, ds1, ds2, current_params, current_regions,
                                        int(step_slider.val), plot_axes, colorbars,
                                        suptitle)

    def on_slider_change(val):
        nonlocal plot_axes, colorbars
        plot_axes, colorbars = plot_map(fig, ds1, ds2, current_params, current_regions,
                                        int(val), plot_axes, colorbars,
                                        suptitle)

    check_param.on_clicked(on_param_change)
    check_region.on_clicked(on_region_change)
    step_slider.on_changed(on_slider_change)

    # initial draw
    plot_axes, colorbars = plot_map(fig, ds1, ds2, current_params, current_regions,
                                    current_step, plot_axes, colorbars,
                                    suptitle)

    plt.show()
