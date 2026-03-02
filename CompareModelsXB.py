# compare XBeach models
# gather multiple output .nc files and compare at target point against expected wave angle
# save a table or visualize as a heat map
# note: heatmap works best with 64 models (4x4x4)


# %%
import os
import re
import glob
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import CenteredNorm


# %% required inputs
filepath='/path_to_nc_files/'
utm_zone = '19S'                                                # project UTM
target_lon = 690983                                             # from breaker depth point
target_lat = 4641308                                            # """
timestep = 2                                                    # ensure spin-up
data_variable = 'thetamean'                                     # wave angle variable name
ShoreNormalWave = 179                                           # assumed nearshore wave angle


# %% check data files
for ncfile in Path(filepath).iterdir():
  if 'jonswap' not in ncfile.name:
    continue
  ncfile.rename(f'{filepath}{ncfile.name[8:13]}{ncfile.name[14:20]}{ncfile.name[21:29]}.nc')
print("Data files in the specified folder:")
os.listdir(filepath)


# %% check utm zone
zone_number = int(utm_zone[:-1])
hemisphere = utm_zone[-1].upper()
if hemisphere == "N":
    epsg_code = 32600 + zone_number
elif hemisphere == "S":
    epsg_code = 32700 + zone_number
else:
    raise ValueError("Invalid UTM zone format. Use format like '33N' or '33S'.")
print(f"Using EPSG:{epsg_code} for UTM Zone {utm_zone}")


# %% find model grid node nearest breaker depth point
randofile = glob.glob(f'{filepath}*.nc', recursive=True)[0]
ds = xr.open_dataset(randofile)

globalx = ds.globalx.values.flatten()
globaly = ds.globaly.values.flatten()
distance = np.sqrt((globalx - target_lon) ** 2 + (globaly - target_lat) ** 2)

closest_flat_idx = np.argmin(distance)
ny, nx = ds.globalx.shape
closest_ny, closest_nx = np.unravel_index(closest_flat_idx, (ny, nx))

actual_lon = ds.globalx.values[closest_ny, closest_nx]
actual_lat = ds.globaly.values[closest_ny, closest_nx]
actual_distance = np.sqrt((actual_lon - target_lon) ** 2 + (actual_lat - target_lat) ** 2)

del randofile
ds.close()

print(f"Target point: ({target_lon}, {target_lat})")
print(f"Closest available data point: ({actual_lon}, {actual_lat})")
print(f"Distance between target point and closest data point: {actual_distance:.2f} meters")


# %% cycle through output .nc files and create dataframe
TempList = []

for ncfile in Path(filepath).iterdir():
  if '.nc' not in ncfile.name:
    continue
  ds = xr.open_dataset(ncfile)
  Hs = float(re.search(r'Hs([\d.]+)Tp', Path(ncfile).name).group(1))
  Tp = float(re.search(r'Tp([\d.]+)Dir', Path(ncfile).name).group(1))
  angle = float(re.search(r'Dir([\d.]+).nc', Path(ncfile).name).group(1))
  DataPoint = ds[data_variable].isel(ny=closest_ny, nx=closest_nx, globaltime=timestep).values
  diff = (DataPoint-ShoreNormalWave)
  TempList.append((Hs, Tp, angle, DataPoint, diff))

df = pd.DataFrame(TempList, columns=["WvHght", "WvPrd", "DirectOffshore", "WvAngle", "TargetDiff"])
df = df.sort_values(by='WvHght')
del TempList
print(df)


# %% save to csv if desired
df.to_csv(Path(filepath).parent / "ModelComparison.csv", index=False, encoding='utf-8')


# %% skip straight to opening csv if saved previously
df = pd.read_csv(Path(filepath).parent / "ModelComparison.csv")
print(df)


# %% results range
print('Range of wave angles at breaker depth point: ')
print(min(df['WvAngle']), '-', max(df['WvAngle']))


# %% visualize results in heatmap
groups = df["WvHght"].unique()
fig, axes = plt.subplots(2, 2, figsize=(10, 10))
axes = axes.flatten()

for i, group in enumerate(groups):
    sub_df = df[df["WvHght"] == group]
    pivot = sub_df.pivot(index="DirectOffshore", columns="WvPrd", values="TargetDiff")

    sns.heatmap(pivot, ax=axes[i], cmap="coolwarm", norm = CenteredNorm(vcenter=0), annot=True, fmt=".2f")
    axes[i].set_title(f"Wave height (m) {(group)}")
    axes[i].invert_yaxis()
    axes[i].set_ylabel('Direction offshore ($^{circ}$)')
    axes[i].set_xlabel('Period (s)')

plt.tight_layout()
plt.show()
