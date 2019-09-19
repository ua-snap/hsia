# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 
# EXAMPLE DOWNLOAD
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 
# 2018 files:

import os

os.chdir('./hsia_updates/nsidc_raw/2018')
username = "LearningToFly"
password = "<ltfpwd>" # insert password here...

for month in ['01','02','03','04','05','06','07','08','09','10','11','12']:
	print( month )
	commanda = 'wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --keep-session-cookies --no-check-certificate --auth-no-challenge=on -r --reject "index.html*" -np -e robots=off --user {} --password {} '.format( username, password )
	commandb = 'https://daacdata.apps.nsidc.org/pub/DATASETS/nsidc0051_gsfc_nasateam_seaice/final-gsfc/north/monthly/nt_2018{}_f17_v1.1_n.bin'.format( month )

	os.system( commanda+commandb )


# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 
# EXAMPLE PROCESSING RUN TO FORMAT FOR HSIA Web Tool
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