# how to run a new HSIA update 
---
## clone the git repo from github
```sh
git clone git@github.com:ua-snap/hsia.git
```

## open that directory
```sh
cd ./hsia
```

## make a virtualenv using python3
```sh
~/.localpython/bin/python3.5 -m venv venv
```

## source in the virtualenv
```sh
source venv/bin/activate
```

## install some packages
```sh
# upgrade pip (this is usually a good choice with a fresh virtualenv)
pip install --upgrade pip

# install package versions this update package needs
pip install -r requirements.txt
```

## install the HSIA package (must be in the repo directory which if following along should be all set.)
```sh
python setup.py install
```

# Now onto the Data Downloading:

## download the files you want to make fit the HSIA app
- this snippet below can be run in an ipython (or similar) interpreter or can be made a `.py` script file and run with `python <name_of_your_scriptfile>.py`
- to get an EarthData Login [register here](https://urs.earthdata.nasa.gov/users/new) with NASA.

```python
# 2018 files:
import os

os.chdir('/workspace/Shared/Tech_Projects/Sea_Ice_Atlas/project_data/hsia_updates/nsidc_raw/2018')
username = "LearningToFly" # insert _your_ EarthData Login here.
password = "<ltfpwd>" # insert _your_ EarthData Password here.

for month in ['01','02','03','04','05','06','07','08','09','10','11','12']:
	print( month )
	commanda = 'wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --keep-session-cookies --no-check-certificate --auth-no-challenge=on -r --reject "index.html*" -np -e robots=off --user {} --password {} '.format( username, password )
	commandb = 'https://daacdata.apps.nsidc.org/pub/DATASETS/nsidc0051_gsfc_nasateam_seaice/final-gsfc/north/monthly/nt_2018{}_f17_v1.1_n.bin'.format( month )

	os.system( commanda+commandb )

```

### UPDATE (on how to download the data):
The above snippet can also be run at the commandline using the function named:`download_nsidc0051.py`
```sh
# for 2018 the command would look something like this:
ipython download_nsidc0051.py -o /workspace/Shared/Tech_Projects/Sea_Ice_Atlas/project_data/hsia_updates/nsidc_raw/2018 -y 2018 -u <your EarthData username> -p <your EarthData password>
```

## Then modify the example run file to fit the year you are running and the proper paths
- this is how it was run to perform the 2018 update.  I would imagine to do the 2019 will be very mmuch the same thing with updated paths to the data and the `years` variable (updated to 2019).

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

# VOILA! This should have produced a new set of data for addition to the HSIA web application.

