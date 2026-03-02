# plot output from XBeach non-hydrostatic model
# initially set up to view water level (individually-resolved waves)
# can be animated - REQUIRES FFMPEG ON LOCAL SYSTEM

# %% import stuff
import os
import glob
import re
import gc
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap

import cmcrameri.cm as cmc
import cmocean.cm as cmo


# %% input parameters
scenario = 'Modern'         # scenario name
sea_level = 0               # scenario sea level
folder = '/path_to_wd/'     # directory path
NCFile = 'FileName.nc'      # XB output file
target_lon = 691983.399     # coordinate within model domain
target_lat = 4641308.501    # coordinate within model domain
utm_zone = '19S'            # UTM zone
data_variable = 'zs'        # variable to plot


# %% gather initial elevation and bathymetry grid
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


# %% find domain boundary corners (in case they're helpful later)
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


# %% plot terrain and bathymetry
norm = mcolors.TwoSlopeNorm(vmin=min_depth, vcenter=sea_level, vmax=max_depth)
cmap = mcolors.LinearSegmentedColormap.from_list(
    "custom_blue_terrain",
    plt.cm.Blues_r(np.linspace(0, 0.7, 128)).tolist() +
    plt.cm.terrain(np.linspace(0.25, 1, 128)).tolist(),
    N=256
)

plt.figure(figsize=(10, 8))
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


# %% load nc output file into dataset
ds = xr.open_dataset(f'{folder}{NCFile}')


# %% check UTM zone
zone_number = int(utm_zone[:-1])
hemisphere = utm_zone[-1].upper()
if hemisphere == "N":
    epsg_code = 32600 + zone_number
elif hemisphere == "S":
    epsg_code = 32700 + zone_number
else:
    raise ValueError("Invalid UTM zone format. Use format like '33N' or '33S'.")
print(f"Using EPSG:{epsg_code} for UTM Zone {utm_zone}")


# %% get data from grid point nearest desired coordinates
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


# %% plot timeseries of variable at target location
plt.figure(figsize=(10, 5))
plt.plot(ds.globaltime, var_time_series, label=ds[data_variable].attrs.get('long_name'))
plt.xlabel("time (s)")
plt.ylabel(data_variable)
plt.title(f"{ds[data_variable].attrs.get('long_name')} at closest grid point ({actual_lon}, {actual_lat})")
plt.legend()
plt.grid(True)
plt.show()


# %% 2D plot at timestep
Var = data_variable         # variable from above
cmap=cmc.oslo               # choose color map
tsec = 1500                 # choose time step
Easting_min = 682000        # limit plotted area
Easting_max = 702000        # limit plotted area
Northing_min = 4632000      # limit plotted area
Northing_max = 4647000      # limit plotted area

X, Y = ds[Var].coords['globalx'], ds[Var].coords['globaly']
land = ds['zb'].sel(globaltime=tsec, method='nearest')
levels = np.linspace(sea_level-0.4, sea_level+0.4, 100)

gc.collect()

plt.figure(figsize=(15, 10))
plt.contourf(X, Y, land, cmap=ListedColormap(['#E8B061']), levels=0, zorder=0)
plt.contour(land.coords['globalx'], land.coords['globaly'], land, colors='black', levels=[0], linewidths=1, zorder=1)
cont = plt.contourf(X, Y, ds[Var].sel(globaltime=tsec, method='nearest'), cmap=cmap, levels=levels, extend='both', zorder=0)
plt.xlim(target_lon-6500, target_lon+6500)
plt.ylim(target_lat-8750, target_lat+2750)
plt.xlabel('Eastings - UTM', horizontalalignment='center')
plt.ylabel('Northings - UTM', horizontalalignment='center')

cbar = plt.colorbar(cont)
cbar.set_label("Zb")

plt.tight_layout()
plt.show()


# %% setup animation
Var = data_variable                     # desired variable
colormap = cmc.oslo                     # color map
Easting_min = target_lon-6500           # restrict area
Easting_max = target_lon+6500           # restrict area
Northing_min = target_lat-8750          # restrict area
Northing_max = target_lat+2750          # restrict area
tstart = 450                            # time subset
tstop = 550                             # time subset
fps = 4                                 # frames per second
output_video_filename = 'OutputVideo.mp4'  # output video name


# %% make stills
outpath = f'{folder}animation/'
img_folder = os.path.join(outpath, 'stills/')
video_path = os.path.join(outpath, 'video/')
os.makedirs(img_folder, exist_ok=True)
os.makedirs(video_path, exist_ok=True)

name = ds[Var].attrs.get('long_name', 'No long_name attribute found')
units = ds[Var].attrs.get('units', 'No long_name attribute found')
time_values = ds.sel(globaltime=slice(tstart, tstop))['globaltime'].values
land = ds['zb'].sel(globaltime=0, method='nearest')
X, Y = ds[Var].coords['globalx'], ds[Var].coords['globaly']

for i, t in enumerate(time_values):
  fig, ax = plt.subplots(figsize=(15, 10))
  ax.contourf(X, Y, land, cmap=ListedColormap(['#E8B061']), levels=0, zorder=0)
  ax.contour(land.coords['globalx'], land.coords['globaly'], land, colors='black', levels=[0], linewidths=1, zorder=1)

  var_array = ds[Var].sel(globaltime=t, method='nearest').values
  cont = ax.contourf(X, Y, var_array, cmap=cmap, levels=levels, extend='both', zorder=0)
  ax.set_xlim(Easting_min, Easting_max)
  ax.set_ylim(Northing_min, Northing_max)
  ax.set_xlabel('Eastings - UTM', horizontalalignment='center')
  ax.set_ylabel('Northings - UTM', horizontalalignment='center')
  cbar = fig.colorbar(cont, ax=ax, label=f"{name} ({units})")
  ax.set_title(f'{name} at t = {t:.1f} s')
  img_filename = os.path.join(img_folder, f"map_{int(i):04d}.jpg")
  plt.savefig(img_filename, format='jpg', dpi=300, bbox_inches='tight')
  plt.clf()
  plt.close(fig)
  del var_array, cont, cbar, ax, fig
  gc.collect()

print(f"Images saved in {img_folder}")


# %% join stills into animation
output_video_file = os.path.join(video_path, output_video_filename)

ffmpeg_cmd = [
    "ffmpeg",
    "-y",
    "-framerate", str(fps),
    "-i", os.path.join(img_folder, 'map_%04d.jpg'),
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-vf", "scale=1920:-2",
    output_video_file
]

print(f"Starting compilation of {i+1} frames at {fps} fps...")

try:
    subprocess.run(ffmpeg_cmd, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    print(f"\n Video successfully created at: {output_video_file}")
except subprocess.CalledProcessError as e:
    print("\n FFmpeg compilation failed.")
    print("STDOUT:", e.stdout.decode())
    print("STDERR:", e.stderr.decode())