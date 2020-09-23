# EXAMPLE RUN
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 
# RUN THE MAIN ACROSS ALL OF THE DATA...

import hsia, os, glob
import numpy as np

template_path = '/workspace/Shared/Tech_Projects/Sea_Ice_Atlas/project_data/hsia_updates/hsia_template/seaice_conc_sic_mean_pct_monthly_ak_1971_04.tif'
template = hsia.TemplateRaster( template_path )
years = [ 2019 ]
for year in years:
    base_path = '/workspace/Shared/Tech_Projects/Sea_Ice_Atlas/project_data/hsia_updates'
    dat_path = os.path.join( base_path, 'nsidc_raw', str(year) )
    output_path = os.path.join( base_path, 'hsia_prepped_v5' )

    if not os.path.exists( output_path ):
        os.makedirs( output_path )

    l = glob.glob( os.path.join( dat_path, '*.bin' ) )
    _ = [ hsia.main( fn, template, output_path ) for fn in l ]

# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 

