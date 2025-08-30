"""
Module for creating interactive weather visualization plots with parameter and region selection.
"""

import logging
from typing import List, Set, Tuple, Any
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from matplotlib.widgets import CheckButtons, Slider

# Configure logging
logging.basicConfig(level=logging.INFO)

# Constants
PARAMETER_NAMES = ["Total Precipitation", "Surface Wind", "Total Cloud Cover"]
REGION_NAMES = ["Global", "Scandinavia"]
SCANDINAVIA_BBOX = [5, 31, 54, 72]
GLOBAL_WIND_SCALE = 700
SCANDINAVIA_WIND_SCALE = 150

# -------------------------------
# Helper functions
# -------------------------------


def setup_widgets(
    fig: plt.Figure, n_steps: int, ds: Any
) -> Tuple[CheckButtons, CheckButtons, Slider]:
    """
    Create parameter, region checkboxes and time slider widgets.

    Args:
        fig: The matplotlib figure to add widgets to.
        n_steps: Number of time steps in the dataset.
        ds: The dataset containing step information.

    Returns:
        Tuple containing parameter checkboxes, region checkboxes, and time slider.
    """
    # Parameter checkbuttons
    ax_param = plt.axes([0.02, 0.5, 0.15, 0.35])
    fig.text(
        0.02 + 0.075,
        0.82,
        "Parameters",
        ha="center",
        va="bottom",
        fontsize=12,
        fontweight="bold",
    )
    check_param = CheckButtons(ax_param, PARAMETER_NAMES, [True, False, False])

    # Region checkbuttons
    ax_region = plt.axes([0.02, 0.25, 0.15, 0.2])
    fig.text(
        0.02 + 0.075,
        0.42,
        "Coverage",
        ha="center",
        va="bottom",
        fontsize=12,
        fontweight="bold",
    )
    check_region = CheckButtons(ax_region, REGION_NAMES, [True, True])

    # Time slider
    ax_slider = plt.axes([0.25, 0.03, 0.65, 0.03])
    slider = Slider(ax_slider, "Time step", 0, n_steps - 1, valinit=0, valstep=1)

    # Tick labels for time steps
    ax_ticks = plt.axes([0.25, 0.03, 0.65, 0.03], frameon=False)
    ax_ticks.set_xlim(0, n_steps - 1)
    ax_ticks.set_xticks(range(0, n_steps, max(1, n_steps // 10)))
    ax_ticks.set_xticklabels([f"{int(s)}h" for s in ds["step"].values / 3600000000000])
    ax_ticks.get_yaxis().set_ticks([])

    return check_param, check_region, slider


def update_params(current_params: Set[str], label: str) -> None:
    """
    Toggle selected parameter.

    Args:
        current_params: Set of currently selected parameters.
        label: Parameter label to toggle.
    """
    if label in current_params:
        current_params.remove(label)
    else:
        current_params.add(label)


def update_regions(current_regions: Set[str], label: str) -> None:
    """
    Toggle selected region.

    Args:
        current_regions: Set of currently selected regions.
        label: Region label to toggle.
    """
    if label in current_regions:
        current_regions.remove(label)
    else:
        current_regions.add(label)


# -------------------------------
# Main plotting logic
# -------------------------------


def plot_map(
    fig: plt.Figure,
    ds1: Any,
    ds2: Any,
    selected_params: Set[str],
    selected_regions: Set[str],
    time_index: int,
    plot_axes: List[Any],
    colorbars: List[Any],
    suptitle: Any,
) -> Tuple[List[Any], List[Any]]:
    """
    Draw the selected parameters and regions at the specified time step.

    Args:
        fig: The matplotlib figure.
        ds1: Global dataset.
        ds2: Scandinavian dataset.
        selected_params: Set of selected parameter names.
        selected_regions: Set of selected region names.
        time_index: Current time step index.
        plot_axes: List of current plot axes to be cleaned up.
        colorbars: List of current colorbars to be cleaned up.
        suptitle: Figure suptitle object.

    Returns:
        Tuple of new plot axes and colorbars lists.
    """
    # Clean up previous plotting axes and colorbars
    for ax in plot_axes:
        fig.delaxes(ax)
    for cbar in colorbars:
        cbar.remove()

    plot_axes = []
    colorbars_new = []

    # Get valid time string from global dataset
    ds_t_global = ds1.isel(step=time_index)
    time_str = str(ds_t_global["tp"].coords["valid_time"].values)[:19].replace(
        "T", ", "
    )

    # Update suptitle
    suptitle.set_y(1.0)
    suptitle.set_x(0.6)
    suptitle.set_text(f"Valid time: {time_str}")

    if not selected_params or not selected_regions:
        fig.canvas.draw_idle()
        return plot_axes, colorbars_new

    # Grid layout
    nrows = len(selected_params)
    ncols = len(selected_regions)
    widths = [1.5 if r == "Global" else 1 for r in selected_regions]
    gs = fig.add_gridspec(
        nrows,
        ncols,
        left=0.25,
        right=0.95,
        top=0.95,
        bottom=0.1,
        hspace=0.25,
        wspace=0.25,
        width_ratios=widths,
    )

    # Loop over parameters and regions
    for i, parameter in enumerate(selected_params):
        for j, region in enumerate(selected_regions):
            ax = fig.add_subplot(gs[i, j], projection=ccrs.PlateCarree())
            plot_axes.append(ax)

            # Select dataset and extent based on region
            if region == "Scandinavia":
                ds = ds2
                extent = SCANDINAVIA_BBOX
                precipitation_var = "rain_con"
            else:  # Global
                ds = ds1
                extent = [
                    ds.longitude.min().item(),
                    ds.longitude.max().item(),
                    ds.latitude.min().item(),
                    ds.latitude.max().item(),
                ]
                precipitation_var = "tp"

            ds_t = ds.isel(step=time_index)
            ax.set_extent(extent, crs=ccrs.PlateCarree())
            ax.add_feature(cfeature.COASTLINE)
            ax.add_feature(cfeature.BORDERS)

            # Plot each parameter
            if parameter == "Total Precipitation":
                _plot_precipitation(
                    ax, ds_t, precipitation_var, region, fig, colorbars_new
                )
            elif parameter == "Surface Wind":
                _plot_wind(ax, ds_t, region, fig, colorbars_new)
            elif parameter == "Total Cloud Cover":
                _plot_cloud_cover(ax, ds_t, region, fig, colorbars_new)

    fig.canvas.draw_idle()
    return plot_axes, colorbars_new


def _plot_precipitation(
    ax: Any,
    ds_t: Any,
    precipitation_var: str,
    region: str,
    fig: plt.Figure,
    colorbars_new: List[Any],
) -> None:
    """Plot precipitation data on the given axes."""
    tp_m = ds_t[precipitation_var] / 1000
    im = tp_m.plot(
        ax=ax,
        cmap="Blues",
        transform=ccrs.PlateCarree(),
        add_colorbar=False,
        vmin=0,
        vmax=0.050,
    )
    cbar = fig.colorbar(
        im,
        ax=ax,
        orientation="vertical",
        pad=0.02,
        fraction=0.04 if region == "Scandinavia" else 0.025,
    )
    cbar.set_label("Total Precipitation (m)")
    colorbars_new.append(cbar)
    ax.set_title(f"Total Precipitation ({region})")


def _plot_wind(
    ax: Any, ds_t: Any, region: str, fig: plt.Figure, colorbars_new: List[Any]
) -> None:
    """Plot wind data on the given axes."""
    skip = (slice(None, None, 10), slice(None, None, 10))
    lats = ds_t["latitude"].values[skip[0]]
    lons = ds_t["longitude"].values[skip[1]]
    u = ds_t["u10"].values[skip]
    v = ds_t["v10"].values[skip]
    Lon, Lat = np.meshgrid(lons, lats)
    wind_speed = np.sqrt(u**2 + v**2)
    scale = SCANDINAVIA_WIND_SCALE if region == "Scandinavia" else GLOBAL_WIND_SCALE
    vmin, vmax = 0, 40
    q = ax.quiver(
        Lon,
        Lat,
        u,
        v,
        wind_speed,
        cmap="coolwarm",
        transform=ccrs.PlateCarree(),
        scale=scale,
        clim=(vmin, vmax),
    )
    cbar = fig.colorbar(
        q,
        ax=ax,
        orientation="vertical",
        pad=0.02,
        fraction=0.04 if region == "Scandinavia" else 0.025,
    )
    cbar.set_label("Wind speed (m/s)")
    colorbars_new.append(cbar)
    ax.set_title(f"Surface Wind ({region})")


def _plot_cloud_cover(
    ax: Any, ds_t: Any, region: str, fig: plt.Figure, colorbars_new: List[Any]
) -> None:
    """Plot cloud cover data on the given axes."""
    im = ds_t["tcc"].plot(
        ax=ax,
        cmap="bone",
        transform=ccrs.PlateCarree(),
        add_colorbar=False,
        vmin=0,
        vmax=100,
    )
    cbar = fig.colorbar(
        im,
        ax=ax,
        orientation="vertical",
        pad=0.02,
        fraction=0.04 if region == "Scandinavia" else 0.025,
    )
    cbar.set_label("Total Cloud Cover (fraction)")
    colorbars_new.append(cbar)
    ax.set_title(f"Total Cloud Cover ({region})")


# -------------------------------
# Entry point function
# -------------------------------


def plot_all_parameters(ds1: Any, ds2: Any) -> None:
    """
    Main function to display interactive weather maps with widgets.

    Args:
        ds1: Global weather dataset.
        ds2: Scandinavian weather dataset.
    """
    try:
        current_params = set(["Total Precipitation"])
        current_regions = set(["Scandinavia", "Global"])
        current_step = 0

        n_steps = len(ds1["step"])
        fig = plt.figure(figsize=(14, 10))

        # Create suptitle (updated every redraw)
        suptitle = fig.suptitle("", fontsize=16)

        # Create widgets
        check_param, check_region, step_slider = setup_widgets(fig, n_steps, ds1)

        # Lists to track plotting axes and colorbars
        plot_axes = []
        colorbars = []

        # Define callback functions
        def on_param_change(label: str) -> None:
            """Handle parameter selection changes."""
            update_params(current_params, label)
            nonlocal plot_axes, colorbars
            plot_axes, colorbars = plot_map(
                fig,
                ds1,
                ds2,
                current_params,
                current_regions,
                int(step_slider.val),
                plot_axes,
                colorbars,
                suptitle,
            )

        def on_region_change(label: str) -> None:
            """Handle region selection changes."""
            update_regions(current_regions, label)
            nonlocal plot_axes, colorbars
            plot_axes, colorbars = plot_map(
                fig,
                ds1,
                ds2,
                current_params,
                current_regions,
                int(step_slider.val),
                plot_axes,
                colorbars,
                suptitle,
            )

        def on_slider_change(val: float) -> None:
            """Handle time slider changes."""
            nonlocal plot_axes, colorbars
            plot_axes, colorbars = plot_map(
                fig,
                ds1,
                ds2,
                current_params,
                current_regions,
                int(val),
                plot_axes,
                colorbars,
                suptitle,
            )

        # Connect callbacks
        check_param.on_clicked(on_param_change)
        check_region.on_clicked(on_region_change)
        step_slider.on_changed(on_slider_change)

        # Initial draw
        plot_axes, colorbars = plot_map(
            fig,
            ds1,
            ds2,
            current_params,
            current_regions,
            current_step,
            plot_axes,
            colorbars,
            suptitle,
        )

        plt.show()
        logging.info("Interactive weather visualization displayed successfully")

    except Exception as exc:
        logging.error(f"Failed to create weather visualization: {exc}")
        raise
