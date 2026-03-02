# plot XB model outputs:
# 1) terrain and bathymetry
# 2) time series of data variable at point 
# 3) 2D variable at timestep


# %% imports
import xarray as xr
import numpy as np
import pandas as pd
import os
import glob
import re
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap
import cmcrameri.cm as cmc
import cmocean


# %% provide inputs
scenario = 'Modern'                     # scenario name
sea_level = 0                           # scenario sea level
folder = '/path_to_working_directory/'  # working directory
BestNC = 'FileName.nc'                  # assumes filename of type "Hs3.0Tp10.0Dir195.0.nc"
target_lon = 691015.270                 # coordinate within model domain
target_lat = 4641459.413                # coordinate within model domain
utm_zone = '19S'                        # UTM zone used
data_variable = 'thetamean'             # variable to plot


# %% gather terrain and bathy info.
x_grd_path = f"{folder}/x.grd"
y_grd_path = f"{folder}/y.grd"
bed_dep_path = f"{folder}/bed.dep"

def parse_grid_data(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        grid_data = [list(map(float, line.split())) for line in lines]
    return np.array(grid_data)

x_grid = parse_grid_data(x_grd_path)
y_grid = parse_grid_data(y_grd_path)
depth_grid = parse_grid_data(bed_dep_path)

min_depth = np.min(depth_grid)
max_depth = np.max(depth_grid)


# %% list corners of model domain (just in case this is helpful later)
rows = np.shape(x_grid)[0]
cols = np.shape(x_grid)[1]

top_left_corner_x = x_grid[0, 0]
top_left_corner_y = y_grid[0, 0]
top_right_corner_x = x_grid[0, cols - 1]
top_right_corner_y = y_grid[0, cols - 1]
bottom_left_corner_x = x_grid[rows - 1, 0]
bottom_left_corner_y = y_grid[rows - 1, 0]
bottom_right_corner_x = x_grid[rows - 1, cols - 1]
bottom_right_corner_y = y_grid[rows - 1, cols - 1]

print(f"Top-Left Corner: ({top_left_corner_x:.2f}, {top_left_corner_y:.2f})")
print(f"Top-Right Corner: ({top_right_corner_x:.2f}, {top_right_corner_y:.2f})")
print(f"Bottom-Left Corner: ({bottom_left_corner_x:.2f}, {bottom_left_corner_y:.2f})")
print(f"Bottom-Right Corner: ({bottom_right_corner_x:.2f}, {bottom_right_corner_y:.2f})")


# %% plot domain
norm = mcolors.TwoSlopeNorm(vmin=min_depth, vcenter=sea_level, vmax=max_depth)
cmap = mcolors.LinearSegmentedColormap.from_list(
    "custom_blue_terrain",
    plt.cm.Blues_r(np.linspace(0, 0.7, 128)).tolist() +
    plt.cm.terrain(np.linspace(0.25, 1, 128)).tolist(),
    N=256
)

plt.figure(figsize=(11, 8))
# hide grid if too dense (turns screen black)
# plt.plot(x_grid, y_grid, color='black', alpha=0.5, linewidth=0.5)
# plt.plot(x_grid.T, y_grid.T, color='black', alpha=0.5, linewidth=0.5)

contour = plt.contourf(x_grid, y_grid, depth_grid, cmap=cmap, norm=norm, levels=50)
cbar = plt.colorbar(contour)
cbar.set_label("Elevation/depth (m)")

plt.xlabel("Eastings - UTM")
plt.ylabel("Northings - UTM")
plt.title(f"{scenario} topo/bathy: SL ~ {sea_level} m")
plt.show()


# %% load nc output file
ds = xr.open_dataset(f'{folder}/{BestNC}')


# %% check UTM zone is good
zone_number = int(utm_zone[:-1])
hemisphere = utm_zone[-1].upper()
if hemisphere == "N":
    epsg_code = 32600 + zone_number
elif hemisphere == "S":
    epsg_code = 32700 + zone_number
else:
    raise ValueError("Invalid UTM zone format. Use format like '33N' or '33S'.")
print(f"Using EPSG:{epsg_code} for UTM Zone {utm_zone}")


# %% get data timeseries from grid point nearest desired coordinates
globalx = ds.globalx.values.flatten()
globaly = ds.globaly.values.flatten()

distance = np.sqrt((globalx - target_lon) ** 2 + (globaly - target_lat) ** 2)
closest_flat_idx = np.argmin(distance)
ny, nx = ds.globalx.shape
closest_ny, closest_nx = np.unravel_index(closest_flat_idx, (ny, nx))
actual_lon = ds.globalx.values[closest_ny, closest_nx]
actual_lat = ds.globaly.values[closest_ny, closest_nx]
actual_distance = np.sqrt((actual_lon - target_lon) ** 2 + (actual_lat - target_lat) ** 2)
var_time_series = ds[data_variable].isel(ny=closest_ny, nx=closest_nx)

print(f"Target point: ({target_lon}, {target_lat})")
print(f"Closest available data point: ({actual_lon}, {actual_lat})")
print(f"Distance between target point and closest data point: {actual_distance:.2f} meters")


# %% plot data variable time series at grid point
plt.figure(figsize=(10, 5))
plt.plot(ds.globaltime, var_time_series, label=ds[data_variable].attrs.get('long_name'))
plt.xlabel("time (s)")
plt.ylabel(data_variable)
plt.title(f"{ds[data_variable].attrs.get('long_name')} at closest grid point ({actual_lon}, {actual_lat})")
plt.legend()
plt.grid(True)
plt.show()


# %% 2D variable plot (note: set up to plot wave direction; modify as desired for other variables)
Var ='thetamean'        # select data variable to plot
tsec = 30               # select timestep in seconds
step = 90               # subsampling factor (reduce density if adding quiver plot)
colormap = cmc.oslo_r   # choose color scheme

name = ds[Var].attrs.get('long_name', 'No long_name attribute found')
units = ds[Var].attrs.get('units', 'No long_name attribute found')
time_values = ds['globaltime'].values
Var_values = ds[Var]
zb_at_time_0 = ds['zb'].sel(globaltime=0)
vmin = Var_values.min().values
vmax = Var_values.max().values*0.6
norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

X, Y = Var_values.coords['globalx'], Var_values.coords['globaly']
VarValSubset = Var_values.sel(globaltime=tsec)[::step, ::step]
Xx = VarValSubset.globalx.values.flatten()
Yy = VarValSubset.globaly.values.flatten()
AngleRad = np.radians(VarValSubset.values.flatten())

u = np.sin(AngleRad+np.pi)
v = np.cos(AngleRad+np.pi)
uu = np.sin(np.radians(var_time_series[2])+np.pi)
vv = np.cos(np.radians(var_time_series[2])+np.pi)

plt.figure(figsize=(13, 9))
plt.contourf(X, Y, zb_at_time_0, cmap=ListedColormap(['#E8B061']), levels=0, zorder=0)
plt.contour(zb_at_time_0.coords['globalx'], zb_at_time_0.coords['globaly'], zb_at_time_0, colors='black', levels=[0], linewidths=1, zorder=1)
cont = plt.contourf(X, Y, Var_values.sel(globaltime=tsec), cmap=colormap, levels=6, zorder=0)
plt.quiver(Xx, Yy, u, v, color='white', scale=40, alpha=1, zorder=1)
plt.quiver(target_lon, target_lat, uu, vv, scale=12, zorder = 1)
plt.annotate(text=f"{round(var_time_series.values[2])}°", xy=(target_lon, target_lat), xytext=(target_lon-1750, target_lat+4000), fontsize=14)
plt.xlabel('Eastings - UTM', horizontalalignment='center')
plt.ylabel('Northings - UTM', horizontalalignment='center')
plt.title(f'Offshore conditions: Hs {Path(BestNC).name[2:5]}m, Tp {Path(BestNC).name[7:10]}s, Dir. {Path(BestNC).name[14:19]}°')

cbar = plt.colorbar(cont)
cbar.set_label("Wave from direction (°)")

plt.tight_layout()
plt.show()