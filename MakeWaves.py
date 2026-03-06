# make a single jonswap.txt file based on a table of satellite altimetry observations


# %% imports
import pandas as pd
import datetime as td
import os


# %% read data, set cwd
workingDirectory = '/path_to_wd/'
waveFile = 'waveFile.csv'
os.chdir(workingDirectory)


# %% bring your own constants!
gammajsp = 3.3
s = 100.0
dtbc = 1.0


# %% clean up dataframe
waves = pd.read_csv(waveFile)
waves.columns = ['datetime', 'height', 'period', 'direction', 'lat', 'lon']
waves['datetime'] = pd.to_datetime(waves['datetime'])
waves


# %% subset by time
startTime = '2017-06-09 00:00:00'
endTime = '2017-06-14 21:00:00'
range = waves[waves['datetime'].between(startTime, endTime)].copy()
range['elapsed'] = range['datetime'] - range['datetime'].min()
range['elapsedseconds'] = range['elapsed'].dt.total_seconds()
range['deltasec'] = range['elapsedseconds'].diff().shift(-1).fillna(1)
range['gammajsp'] = gammajsp
range['s'] = s
range['dtbc'] = dtbc
del waves
range


# %% organize into XBeach-style JONSWAP table
waveTable = range[['height', 'period', 'direction', 'gammajsp', 's', 'deltasec', 'dtbc']].round(2)
del range
waveTable


# %% write text file
waveTable.to_csv('jonswap.txt', sep=' ', index=False, header=False)
