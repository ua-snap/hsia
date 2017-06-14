### HSIA
##### prepare raw NSIDC_0051 .bin sea ice concentration (SIC) files for Historical Sea Ice Atlas

See `example.py` for the way that we run this tool. Basic use is to change the year(s) and output_path
in that script and point to the `.bin` files downloaded from the NSIDC-0051.

requires a NASA EarthData Login for access to the files.

*EXAMPLE FILE ACCESS FROM NEW HTTPS STORAGE AT NSIDC/NASA*
```python
# 2016 files:
import os

os.chdir('./hsia_updates/nsidc_raw/2016')
username = "LearningToFly"
password = "<ltfpwd>" # insert password here...

for month in ['01','02','03','04','05','06','07','08','09','10','11','12']:
	print( month )
	commanda = 'wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --keep-session-cookies --no-check-certificate --auth-no-challenge=on -r --reject "index.html*" -np -e robots=off --user {} --password {} '.format( username, password )
	commandb = 'https://daacdata.apps.nsidc.org/pub/DATASETS/nsidc0051_gsfc_nasateam_seaice/final-gsfc/north/monthly/nt_2016{}_f17_v1.1_n.bin'.format( month )

	os.system( commanda+commandb )
```

See the `run2016_hsia.py` file for the way we ran the 2016 data.


