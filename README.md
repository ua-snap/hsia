# Historical Sea Ice Atlas

This repository is for creating the data available in SNAP's [Historical Sea Ice Atlas (HSIA) dataset](http://ckan.snap.uaf.edu/dataset/historical-sea-ice-atlas-observed-estimates-of-sea-ice-concentration-in-alaska-waters), which contains gridded sea ice concentrations for the waters surrounding Alaska. 

In the past, this repo had previously been used for updating the data displayed in SNAP's [Historical Sea Ice Atlas webapp](https://www.snap.uaf.edu/tools/sea-ice-atlas), as the above dataset was previously the ingest data for that webapp. However, the newest version of the webapp makes use of [panarctic data](https://nsidc.org/data/g10010), so this repo is now dedicated to the "Alaska" HSIA dataset only. 

## Updating the Historical Sea Ice Atlas dataset

The [update_hsia.ipynb](update_hsia.ipynb) jupyter notebook contains step-by-step instructions for downloading new data from the NSIDC, running this codebase on it, and some unix commands for organizing it with previous versions on SNAP's systems. The goal of the updates is to integrate new releases of the [NSIDC-0051 dataset](https://nsidc.org/data/nsidc-0051), which occurs annually.

This repository has been updated to use `anaconda-project`, which can be installed via `conda` with `conda install anaconda-project`. 

To run the jupyter notebook used for updating the HSIA dataset, simply run `anaconda-project run update_hsia`, and follow the instructions therein.

**Note** - There are existing paths hard-coded into the processing code that is imported into the notebook. In it's current state, this codebase should only be run via machines with a connection to the Poseidon server via (`/workspace/`) 

## Contents

`hsia/`: The code for processing the downloaded data to the standardized format used for the HSIA dataset. 
`archive/`: Old code and things that might be useful to have, mostly for SNAP internal purposes.
