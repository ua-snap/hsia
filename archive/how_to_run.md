# How To Run package:`hsia`

## ABOUT
This package is a simple way for SNAP to access data from the NSIDC-0051 Monthly data archive [see here](https://catalog.data.gov/dataset/sea-ice-concentrations-from-nimbus-7-smmr-and-dmsp-ssm-i-ssmis-passive-microwave-data-v001/resource/88927a8a-eeb2-4510-8f08-a4b9cd6bff16), and process it to fit the needed scale, area of interest, and coordinate reference system of the [Historical Sea Ice Atlas](http://seaiceatlas.snap.uaf.edu/).


## INSTALLATION
### clone github repo and enter directory
```sh
git clone git@github.com:ua-snap/hsia.git
cd ./hsia
```

### make python3 virtualenv and source it in 
```sh
~/.localpython/bin/python3 -m venv venv
source venv/bin/activate
```

### packages install using `pip`
```sh
# upgrade pip (this is usually a good choice with a fresh virtualenv)
pip install --upgrade pip

# install package versions this update package needs
pip install -r requirements.txt
```

### install the `hsia` package -- using the setup.py file in its repo
```sh
python setup.py install
```


## DOWNLOAD NSIDC-0051 Monthly Data

### access the data
This requires a NASA EarthData Login. To get one [register here](https://urs.earthdata.nasa.gov/users/new) with NASA.
- see the `[example.py](https://github.com/ua-snap/hsia/blob/master/example.py)` file in the root directory of this repository for explicit ways of downloading without the CLI below.
- use `download_nsidc0051.py` to download the data you want for a selected year. _For 2019, you should be able to just change the year in the paths and `-y` flag below._
```sh
# for 2018 the command would look something like this:
pipenv run python download_nsidc0051.py -o /workspace/Shared/Tech_Projects/Sea_Ice_Atlas/project_data/hsia_updates/nsidc_raw/2019 -y 2019 -u <your EarthData username> -p "<your EarthData password>"
# (password in quotes to deal with special characters, e.g. parentheses)
```

### process the data for `hsia` ingest
- see `[example.py](https://github.com/ua-snap/hsia/blob/master/example.py)` for more information on how this was run for the last year we ran it (2018).

Below is how the launcher looked for the 2018 data prep:
```python
# EXAMPLE RUN
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 
# RUN THE MAIN ACROSS ALL OF THE DATA...

import hsia, os, glob
import numpy as np

template_path = '/workspace/Shared/Tech_Projects/Sea_Ice_Atlas/project_data/hsia_updates/hsia_template/seaice_conc_sic_mean_pct_monthly_ak_1971_04.tif'
template = hsia.TemplateRaster( template_path )
years = [ 2018 ]
for year in years:
	base_path = '/workspace/Shared/Tech_Projects/Sea_Ice_Atlas/project_data/hsia_updates'
	dat_path = os.path.join( base_path, 'nsidc_raw', str(year) )
	output_path = os.path.join( base_path, 'hsia_prepped_v4' )

	if not os.path.exists( output_path ):
		os.makedirs( output_path )

	l = glob.glob( os.path.join( dat_path, '*.bin' ) )
	_ = [ hsia.main( fn, template, output_path ) for fn in l ]

# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 
```

##### VOILA! This should have produced a new set of data for addition to the HSIA web application.

