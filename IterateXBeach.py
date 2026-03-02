# repeatedly run XBeach over a directory of JONSWAP files
# creates a unique .nc output file for each JONSWAP file
# assumes JONSWAP files have been named by MakeJONSWAPS.py script

# %%
import os
import shutil
import subprocess
from pathlib import Path

# %%
XBfolder = 'path_to_model_directory'
JSWPfolder = 'directory_containing_JONSWAPs'

# %%
XBpath = Path(XBfolder) / 'xbeach.exe'
XBpath = f'"{XBpath}"'
JSdone = Path(XBfolder) / 'jonswapDone/'
CDFdone = Path(XBfolder) / 'OutputsNetCDF/'

Path(JSdone).mkdir(exist_ok=True)
Path(CDFdone).mkdir(exist_ok=True)

FileCount = 0
for JSfile in Path(JSWPfolder).iterdir():
  if 'jonswap_Hs' not in JSfile.name:
    continue
  FileCount += 1

print(f'Path to xbeach.exe: {XBpath}')
print(f'Completed jonswap.txt files will go here: {JSdone}')
print(f'NetCDF output files will go here: {CDFdone}')
print(f'Prepare to run xbeach.exe {FileCount} times...')

# %%
print('Starting XBeach runs...')

for JSfile in Path(JSWPfolder).iterdir():
    if '.emplate' in JSfile.name:
        continue
    fname = JSfile.stem
    JSpath1 = Path(XBfolder) / JSfile.name
    JSpath2 = Path(XBfolder) / 'jonswap.txt'
    JSpath3 = Path(JSdone) / 'jonswap.txt'
    JSpath4 = Path(JSdone) / f'{fname}.txt'
    CDFpath1 = Path(XBfolder) / 'xboutput.nc'
    CDFpath2 = Path(CDFdone) / 'xboutput.nc'
    CDFpath3 = Path(CDFdone) / f'{fname}.nc'

    shutil.move(JSfile, JSpath1)
    JSpath2.unlink(missing_ok=True)
    JSpath1.rename(JSpath2)

    subprocess.run(XBpath, shell=True)

    shutil.move(JSpath2, JSpath3)
    JSpath4.unlink(missing_ok=True)
    JSpath3.rename(JSpath4)

    shutil.move(CDFpath1, CDFpath2)
    CDFpath3.unlink(missing_ok=True)
    CDFpath2.rename(CDFpath3)

print('Finished XBeach runs.')
print(f'Moved jonswap files to {JSdone} folder.')
print(f'Moved NetCDF output files to {CDFdone} folder.')