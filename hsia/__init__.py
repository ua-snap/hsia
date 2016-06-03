import hsia
from hsia.seaice import SeaIceRaw, TemplateRaster
from hsia import utils
import rasterio, os
import numpy as np

def get_padded_shape( full_rst, template, resolution, output_filename ):
	'''
	object of type Template Raster and return a padded shapefile extent to use in clipping
	this is a function to be run once and use the same clipper shapefile throughout the processing.

	we are using gdalwarp and other gdal commandline utilities here because they are fast, already 
	implemented, and work well dealing with many polar reference systems and conversions.

	ARGUMENTS:
	----------
	template = [hsia.TemplateRaster] TemplateRaster object
	resolution = [numeric] resolution

	RETURNS:
	--------
	[str] name of the output shapefile extent created which can be used in later gdalwarp commands
	as the cutline feature.  These are some hacks to get around some really funky issues going 
	between polar and 'normal' projections.

	'''	
	template_out_fn = template.fn.replace( '.tif', '_epsg3413.tif' )
	os.system( "gdalwarp -overwrite -s_srs EPSG:4326 -t_srs EPSG:3413 -of GTiff -r near -tr " + str( resolution ) + " " + str( resolution ) + " " + \
				template.fn + ' ' + template_out_fn )

	template_3413 = rasterio.open( template_out_fn )
	new_shp_fn = padded_extent_to_shp( full_rst, template_3413, (0,0,5,0),  "EPSG:3413", output_filename )
	return new_shp_fn

def drop_erroneous_ice( fn, fn_list, output_path ):
	import pandas as pd
	
	cur = rasterio.open( fn )
	cur_arr = cur.read( 1 ).astype( int )

	# booleanize
	cur_bool = cur_arr.copy()
	cur_bool[ cur_bool > 0 ] = 1

	# file metadata
	meta = cur.meta
	meta.update( compress='lzw', nodata=128, dtype='uint8' )
	if 'transform' in meta.keys():
		meta.pop( 'transform' )
	
	# stack up the timesteps rasters for the full period
	all_files = pd.Series( fn_list )
	# all_files_grouped = all_files.groupby( [ i.split('.')[0].split('_')[-1] for i in all_files ] )
	# stack = np.array([ rasterio.open( i ).read( 1 ) for i in all_files_grouped.get_group( month ) \
	# 		if (int(i.split('.')[0].split('_')[-2]) >= 1979) & (int(i.split('.')[0].split('_')[-2]) <= 2012) ])

	stack = np.array( [ rasterio.open( i ).read(1) \
						for i in all_files if (int(i.split('.')[0].split('_')[-2]) >= 1979) & \
						(int(i.split('.')[0].split('_')[-2]) <= 2012) ] )
	
	# some data prep
	stack[ stack > 0 ] = 1
	stack = stack.astype( np.int32 )
	stack = stack.sum( axis=0 )
	
	# booleanize
	stack[ stack > 0 ] = 1
	
	# compare
	diff = stack - cur_bool
	cur_arr[ (diff == -1) & (cur_arr <= 100) ] = 0

	# set the quality flags in band 2
	# cur_arr2 = cur.read( 2 )
	# cur_arr2[ (diff == -1) & (cur_arr <= 100) ] = 99 # some value and document this.

	# write it out to disk:
	# output_path = '/workspace/Shared/Tech_Projects/Sea_Ice_Atlas/project_data/update_2014/hsia_2014_update_gtiffs_dropice_v2'
	output_filename = os.path.join( output_path, os.path.basename( cur.name ).replace( '.tif', '_dropice_v2.tif' ) )

	with rasterio.open( output_filename, 'w', **meta ) as out:
		out.write( cur_arr.astype( np.uint8 ), 1 )
		# out.write( cur_arr2, 2 )

	return output_filename

def main( fn, template, output_path=None ):
	'''
	main function for running this script with the NSIDC 0051 2014-2015 update to HSIA

	This codebase is mainly to keep it all clean and in one place for when we need to approach it
	again, which is always sooner than later.  :)

	'''
	import rasterio, glob, os

	# convert `.bin` to `.tif` in 3413
	sic = SeaIceRaw( fn )
	sic_fn = sic.to_gtiff_3413()
	resolution = str( sic.get_metadata()['affine'].a ) # 25000

	# return padded extent for clipping
	pad_fn = template.fn.replace( '.tif', '_padext.shp' )
	if os.path.exists( pad_fn ):
		os.unlink( pad_fn )

	full_rst = rasterio.open( sic_fn )
	pad_ext = get_padded_shape( full_rst, template, resolution, pad_fn )

	# gdalwarp to crop to new padded extent
	os.system( "gdalwarp -q -overwrite -s_srs EPSG:3413 -t_srs EPSG:3413 -tap -cutline " + pad_ext + \
				" -crop_to_cutline -tr 25000 25000 -te "+ \
				str(list(full_rst.bounds)).strip('[').strip(']').replace( ', ', ' ') + " " + \
				full_rst.name + " " + full_rst.name.replace( '.tif', '_hsia.tif' ) )

	# read data back in and set all nodata values to 255
	with rasterio.open( full_rst.name.replace( '.tif', '_hsia.tif' ) ) as rst:
		arr = rst.read( 1 )
		meta = rst.meta

	meta.update( compress='lzw', dtype=rasterio.uint8, nodata=255 )
	with rasterio.open( rst.name, 'w', **meta ) as rst:
		arr[ arr > 250 ] = 255
		rst.write_band( 1, arr )

	# reproject to HSIA extent / resolution / reference system
	output_filename = rst.name.replace( '3413', '4326' )
	os.system( "gdalwarp -q -overwrite -s_srs EPSG:3413 -t_srs EPSG:4326 -of GTiff -ot Int16 \
				-te -180.0 40.0 -119.75 80.25 -tr 0.25 -0.25 -r bilinear -srcnodata 255 -dstnodata 255 " + 
				rst.name
				+ " " + 
				output_filename )

	# read in the masks from the 2 groups
	hsia_mask_arr = template.get_mask()
	nsidc_mask_arr = (rasterio.open( output_filename ).read(1) == 255).astype( int )
	
	# now lets add in some data to the metadata layer...
	# read in some FINALIZED data
	sic_conv = rasterio.open( output_filename )
	sic_arr = sic_conv.read( 1 )

	# pull the mask of 255 off of the data we just read in so we can use it in the source band 
	# for some identification of modified pixels.
	sic_arr_mask = (sic_arr == 255).astype( np.int16 )

	# mask it
	sic_arr[ hsia_mask_arr == 1 ] = 128
	
	# # read in the warping artifact due to extent diffs
	# artifact = rasterio.open( warp_artifact_mask_fn )
	# artifact_arr = artifact.read( 1 )
	
	# perform diff between the masks
	diff_arr = nsidc_mask_arr - hsia_mask_arr
	fill_mask = (diff_arr == 1).astype( np.uint8 )
	# fill_mask = np.zeros_like( diff_arr )
	# fill_mask[ diff_arr == 1 ] = diff_arr[ diff_arr == 1 ]

	# TMP output -- THIS IS AN IMPORTANT MASK THAT NEEDS TO BE USED IN THE REPLACEMENT OF ERRANT PIXELS...
	# -1 = fill with surrounding pixel values between 1-100
	# 0 = other areas
	# 1 = inland lakes and inlets not covered by the NSIDC landmask, but present in the HSIA mask

	# run fill with recursion
	sic_arr = fill_mask_mismatch( sic_arr, np.copy( fill_mask ) )

	# WRITE OUT FINAL GTIFF PREPPED FOR HSIA WITHOUT ERROR ICE REMOVED
	meta = sic_conv.meta
	meta.update( compres_convs='lzw' )
	output_filename = sic_conv.name.replace( '.tif', '_filled2.tif' ) # FINAL PRE-DROPICE NAME HERE
	with rasterio.open( output_filename, 'w', **meta ) as out:
		out.write( sic_arr, 1 )

	# drop erroneous sea ice:
	month = output_filename.split('_')[1][4:] # HARDWIRED AND DANGEROUS STUFF HERE!
	output_path = '/workspace/Shared/Tech_Projects/Sea_Ice_Atlas/project_data/update_2014/hsia_2014_update_gtiffs_dropice_v2'
	fn_list = glob.glob( '/workspace/Shared/Tech_Projects/Sea_Ice_Atlas/project_data/HSIA_SIC_Chapman/v1_0/monthly/gtiff/*'+month+'.tif' )
	# this output SHOULD be the final good-to-go output TESTS NEEDED HERE!
	sic_out_fn = drop_erroneous_ice( out.name, fn_list, output_path )

	# BUILD OUT THE SOURCE BAND (2)
	# PIXEL TYPES:
	NSIDC_0051 = 8
	filled_recursive = 23
	missing_data_inland = 22
	ice_dropped_with_historical = 24 # (?)
	landmask = 128

	# OPEN THE DATE JUST CREATED AND MAKE A NEW EMPTY BAND FROM ITS ARRAY SHAPE
	final_sic = rasterio.open( sic_out_fn )
	final_arr = final_sic.read( 1 )
	source_arr = np.empty_like( final_arr )

	# # THIS IS A HACK!!!
	# diff_arr = nsidc_mask_arr - hsia_mask_arr
	# fill_mask = (diff_arr == 1).astype( np.uint8 )

	# FILL IT IN WITH THE NEW VALUES
	source_arr[ hsia_mask_arr != 1 ] = NSIDC_0051 # set all pixels to the NSIDC 0051 data group and we will update from here
	source_arr[ final_arr == 128 ] = landmask
	source_arr[ fill_mask == 1 ] = filled_recursive
	source_arr[ final_arr == 255 ] = missing_data_inland

	# dropped ice...  How to do this?
	diff_final = sic_arr - final_arr
	diff_final[ diff_final != 0 ] = 1
	source_arr[ diff_final == 1 ] = ice_dropped_with_historical

	# WRITE OUT FINAL GTIFF PREPPED FOR HSIA WITH ERROR ICE REMOVED
	meta = final_sic.meta
	meta.update( compress='lzw', dtypes=['uint8', 'uint8'], dtype='uint8', count=2, nodata=255 )
	output_filename = final_sic.name.replace( '.tif', '_dropice.tif' ) # FINAL NAME HERE
	with rasterio.open( output_filename, 'w', **meta ) as out:
		out.write( final_arr, 1 )
		out.write( source_arr, 2 )

	return output_filename


	meta = final_sic.meta
	meta.update( compress='lzw', dtype='uint8', nodata=255 )
	output_filename = final_sic.name.replace( '.tif', '_FILLMASK.tif' ) # FINAL NAME HERE
	with rasterio.open( output_filename, 'w', **meta ) as out:
		out.write( fill_mask, 1 )

# template_path = '/workspace/Shared/Tech_Projects/Sea_Ice_Atlas/project_data/hsia_updates/hsia_template/seaice_conc_sic_mean_pct_monthly_ak_1971_04.tif'
# # for input_fn in glob.glob( os.path.join( input_path, '*.bin' ) ):
# def run( fn, template_fn ):
# 	sic = SeaIceRaw( fn )
# 	sc_fn = sic.to_gtiff()
# 	template = TemplateRaster( template_fn )

# 	# reproject the NSIDC data to EPSG:3413 using gdal
# 	resolution = sic.get_metadata()['affine'][0] # 25000
# 	out_fn = sic.fn.replace( '.tif', '_epsg3413.tif' )
# 	os.system( "gdalwarp -overwrite -s_srs " + sic.crs + " -t_srs EPSG:3413 -of GTiff -r near -tr " + \
# 				str( resolution ) + " " + str( -resolution ) + " " + \
# 				sic.fn + ' ' + \
# 				out_fn )

# 	# procedure
# 	# convert reprojected HSIA to 3413 extent to a shapefile with a padded extent 
# 	#  this is for clipping the NSIDC rasters using gdalwarp 
# 	full_rst = rasterio.open( out_fn )
# 	proj4string = "EPSG:3413"
# 	template_out_fn = template.fn.replace( '.tif', '_epsg3413.tif' )
	
# 	# project the template raster to the 3413 in the template extent
# 	os.system( "gdalwarp -overwrite -s_srs EPSG:4326 -t_srs EPSG:3413 -of GTiff -r near -tr " + str( resolution ) + " " + str(-resolution) + " " + \
# 				template.fn + ' ' + template_out_fn )

# 	template_3413 = rasterio.open( template_out_fn )
# 	new_shp_fn = utils.padded_extent_to_shp( full_rst, template_3413, (0,0,5,0), proj4string, output_shapefile )
	
# 	# now lets gdalwarp to crop to this new domain
# 	os.system( "gdalwarp -overwrite -s_srs EPSG:3413 -t_srs EPSG:3413 -tap -cutline " + new_shp_fn + " -crop_to_cutline -tr 25000 -25000 -te "+ \
# 				str(list(full_rst.bounds)).strip('[').strip(']').replace( ', ', ' ') + " " + full_rst.name + " " + \
# 				full_rst.name.replace( '.tif', '_hsia.tif' ) )

# 	# read the data back in and set all nodata numbers to 255
# 	rst = rasterio.open( full_rst.name.replace( '.tif', '_hsia.tif' ) )
# 	arr = rst.read( 1 )
# 	meta = rst.meta
# 	meta.update( compress='lzw', dtype=rasterio.uint8, nodata=255 )
# 	rst.close()

# 	with rasterio.open( rst.name, 'w', **meta ) as rst:
# 		nodata_locs = np.where( arr > 250 )
# 		nodata_vals = arr[ nodata_locs ]
		
# 		arr = np.divide( arr.astype( np.float32 ), 250 )
# 		arr = (arr * 100).astype( np.uint8 )
# 		arr[ nodata_locs ] = nodata_vals

# 		arr[ arr > 250 ] = 255
# 		rst.write_band( 1, arr )

# 	# now lets project it back to the HSIA extent / resolution / reference system
# 	output_filename = rst.name.replace( '3413', '4326' )
# 	os.system( "gdalwarp -overwrite -s_srs EPSG:3413 -t_srs EPSG:4326 -of GTiff -ot Int16 \
# 				-te -180.0 40.0 -119.75 80.25 -tr 0.25 -0.25 -r bilinear -srcnodata 255 -dstnodata 255 " + 
# 				rst.name
# 				+ " " + 
# 				output_filename )

	# # fill in a copy of the template landmask raster
	# fn_date = os.path.basename(full_rst.name).split('_')[1]
	# fn_date = '_'.join([fn_date[:4], fn_date[4:]])
	# new_rst_fn = os.path.join( output_path, 'seaice_conc_sic_mean_pct_monthly_ak_'+fn_date+'_FINALIZE.tif')
	# # copy the data to a new file
	# processed_rst = rasterio.open( output_filename )
	# processed_arr = processed_rst.read( 1 ).data
	# meta = processed_rst.meta
	# meta.update( compress='lzw', dtype=rasterio.int16, nodata=-128, crs={'init':'EPSG:4326'} )
	# # open the landmask:
	# with rasterio.open( hsia_data_mask ) as landmask:
	# 	landmask_arr = landmask.read( 1 ).data.astype( rasterio.int16 )
	# 	with rasterio.open( new_rst_fn, 'w', **meta ) as out_rst:
	# 		landmask_arr[ landmask_arr != 0 ] = -128 # make the land -128
	# 		ind = np.where( (processed_arr > 0) & (processed_arr < 250) & (landmask_arr != -128) )
	# 		landmask_arr[ ind ] = processed_arr[ ind ]
	# 		out_rst.write_band( 1, landmask_arr )

