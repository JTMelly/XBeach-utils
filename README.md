# XB-utils

### Utilities for setting up and running XBeach models and interacting with their outputs.

## Notes:

Some of these tools were modified from the [Coastal Hydrodynamics](https://github.com/Alerovere/CoastalHydrodynamics) toolbox by [Alerovere](https://github.com/Alerovere). Others are loosely based on vibe-coded prototypes that have hopefully been made functional. The goal is a set of small, individual tools that can be used alone or inserted into larger programs.

Scripts are mostly *Python* and should work as *Jupyter Notebooks* or in *Colabs* with limited tinkering. Blocks of code are organized into interactive chunks because we debug in production.

To use these tools, some typical packages needed may include:  
```
- xarray
- pandas
- netcdf4
- scipy
```
The above list is not comprehensive; a *yaml* file may be forthcoming as time permits. In the meantime, [conda-forge](https://conda-forge.org/) seems like a good option for consistent dependencies.

## Find breaker depth
`FindBreakerDepth.py` estimates wave breaker depth given model sea level and some spectral wave statistics. Breaker depth may be needed later to identify a single model grid node at which to compare model results. A use case might be:
1) estimate beach slope, offshore wave height, wavelength, and celerity using expert opinion, published values, or other software tools;
2) calculate breaker depth based on the above estimates using `FindBreakerDepth.py`;
3) locate the coordinates of an ideal breaker depth point in *GIS* by drawing a line through the shoreline downdrift control point following the assumed dominant nearshore wave approach angle&mdash;the intersection of this line and the breaker depth contour gives the idealized breaker depth point;
4) use the breaker depth coordinates to compare model results using `CompareModelsXB.py`

## Make non-erodible layer

`NonErodibleLayer.py` takes a *bed.dep* file and essentially replaces all the elevation values with "0." Saves a new *.dep* file in the same location as the orginal *bed.dep* file. The new file can be called in the XBeach model's *params.txt* file. This will produce the effect of no erosion/sedimentation throughout the model run.

## Make JONSWAP files

`MakeJONSWAPs.py` makes a whole mess of *jonswap* files with unique names based on wave boundary conditions. The user supplies arrays of desired wave height, wave period, and wave direction and the script creates a unique file for each permutation. These files can be called later by `IterateXBeach.py` to run XBeach for each combination of wave boundary conditions.

## Run XBeach repeatedly

`IterateXBeach.py` runs `xbeach.exe` one time for each *jonswap* file created by `MakeJONSWAPs.py`. *NetCDF* output files are named according to model boundary conditions and collected in a dedicated directory.

## Compare XBeach models
Use `CompareModelsXB.py` to compare the results of all the models produced by `IterateXBeach.py`, above. This script scans through all of the *NetCDF* output files in a directory and extracts the solutions at some desired coordinates and for a given timestep. These values are gathered in a dataframe for comparison against expected values and/or graphical visualizaion. 
