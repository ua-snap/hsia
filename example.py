# EXAMPLE RUN
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 
# RUN THE MAIN ACROSS ALL OF THE DATA...

years = [ 2014, 2015 ]
for year in years:
	dat_path = os.path.join( '/workspace/Shared/Tech_Projects/Sea_Ice_Atlas/project_data/hsia_updates', str(year), 'raw' )
	out_path = os.path.join( '/workspace/Shared/Tech_Projects/Sea_Ice_Atlas/project_data/hsia_updates', str(year), 'prepped' )
	l = glob.glob( os.path.join( dat_path, '*.bin' ) )
	_ = [ main( fn, template, output_path ) for fn in l ]

# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 
