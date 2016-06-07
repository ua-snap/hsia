# utility functions for use in the processing from raw NSIDC data to HSIA format
import numpy as np

def bounds_to_extent( bounds ):
	'''
	take input rasterio bounds object and return an extent
	'''
	l,b,r,t = bounds
	return [ (l,b), (r,b), (r,t), (l,t), (l,b) ]

def extent_to_shapefile( extent, output_shapefile, proj4string ):
	''' convert an extent to a shapefile using its proj4string '''
	import geopandas as gpd
	from shapely.geometry import Polygon
	gpd.GeoDataFrame( {'extent_id':1, 'geometry':Polygon( extent )}, index=[1], crs=proj4string ).to_file( output_shapefile, 'ESRI Shapefile' )
	return output_shapefile

def coordinates( fn ):
	'''
	take a raster file as input and return the centroid coords for each 
	of the grid cells as a pair of numpy 2d arrays (longitude, latitude)
	'''
	import rasterio
	import numpy as np
	from affine import Affine
	from pyproj import Proj, transform

	# Read raster
	with rasterio.open(fn) as r:
		T0 = r.affine  # upper-left pixel corner affine transform
		p1 = Proj(r.crs)
		A = r.read(1)  # pixel values

	# All rows and columns
	cols, rows = np.meshgrid(np.arange(A.shape[1]), np.arange(A.shape[0]))

	# Get affine transform for pixel centres
	T1 = T0 * Affine.translation(0.5, 0.5)
	# Function to convert pixel row/column index (from 0) to easting/northing at centre
	rc2en = lambda r, c: (c, r) * T1

	# All eastings and northings (there is probably a faster way to do this)
	eastings, northings = np.vectorize(rc2en, otypes=[np.float, np.float])(rows, cols)

	# Project all longitudes, latitudes
	longs, lats = transform(p1, p1.to_latlong(), eastings, northings)
	return longs, lats

def padded_extent_to_shp( rst1, rst2, npixels, crs, output_shapefile ):
	'''
	convert the extents of 2 overlapping rasters to a shapefile with 
	an expansion of the intersection of the rasters extents by npixels

	rst1: rasterio raster object
	rst2: rasterio raster object
	npixels: tuple of 4 (left(-),bottom(-),right(+),top(+)) number of pixels to 
		expand in each direction. for 5 pixels in each direction it would look like 
		this: (-5. -5. 5, 5) or just in the right and top directions like this:
		(0,0,5,5).
	crs: epsg code or proj4string defining the geospatial reference 
		system
	output_shapefile: string full path to the newly created output shapefile

	'''
	import rasterio, os, sys
	from shapely.geometry import Polygon

	# rst to pols
	resolution = rst1.res[0]
	ext1 = bounds_to_extent( rst1.bounds )
	ext2 = bounds_to_extent( rst2.bounds )
	pol1 = Polygon( ext1 )
	pol2 = Polygon( ext2 )

	isect_ext_pol = pol1.intersection( pol2 )
	new_bounds = [ bound+(expand*resolution) for bound, expand in zip( isect_ext_pol.bounds, npixels ) ]
	
	new_ext = bounds_to_extent( new_bounds )
	return extent_to_shapefile( new_ext, output_shapefile, crs )

def fill_mask_mismatch( sic_arr, diff_arr, count_missing=(0,1) ):
	'''
	recurse through the sea ice array and the error locations array
	and fill in the missing data that is not inland as the mean of 
	the surrounding (queens case) pixels truncated to an integer.

	dont mind the count_missing variable, it is simply a placeholder 
	that is used in storing some information during the recursion. 
	I'm sure there is better practice here but this is elegant enough
	for this application (small raster sizes).

	all other values inland are returned as value 255

	returns a filled sea ice array that can be easily written to disk
	using rasterio.

	'''
	height, width = sic_arr.shape
	arr = np.copy( diff_arr ) # since we update the array, make sure its not a view...
	# grab the index of the error locations
	ind = np.where( arr == 1 )
	ind = zip( *ind )
	count1, count2 = count_missing
	# print count_missing
	if count1 == count2:
		# fill in the remainders with 255 and return
		for ii in ind:
			sic_arr[ ii ] = 255
		return sic_arr
	else:
		# fill em if we can, if not, make em 255 -- we could use more neighbors but that sounds hairy
		# all_missing_neighbors = {(i,j):[ (i-1,j+0), (i+0,j-1), (i+0,j+1), (i+1,j+0) ] for i,j in ind } # rooks
		all_missing_neighbors = { (i,j):[ (i-1,j+0), (i+0,j-1), (i+0,j+1), (i+1,j+0), (i+1,j+1), \
									(i-1,j+1), (i-1,j-1), (i+1,j-1) ] for i,j in ind } # queens

		for missing, neighbors_list in all_missing_neighbors.iteritems():
			nlist = neighbors_list # just hold the name for testing
			nlist = [ (i,j) for i,j in nlist if i >= 0 and i < height if j >= 0 and j < width ]
			# vals = np.array( [ sic_arr[ n ].tolist() for n in nlist if n != None if sic_arr[ n ] != 128 if sic_arr[ n ] != 255 if sic_arr[ n ] != 0  ])
			vals = np.array([ sic_arr[ n ].tolist() for n in nlist if n != None if sic_arr[ n ] != 128 if sic_arr[ n ] != 255 ]) #if sic_arr[ n ] != 0 
			# vals = np.array( [ sic_arr[ n ].tolist() for n in nlist if n != None if sic_arr[ n ] != -128 if sic_arr[ n ] != 255 if sic_arr[ n ] != 0  ])
			
			vals = vals[ vals >= 0 ].tolist()
			if len( vals ) == 0:
				# print 255
				new_val = 255
				arr[ missing ] = 1 # keep flag for missing
			elif len( vals ) > 0 :
				new_val = int( np.mean( vals ) )
				arr[ missing ] = 0 # remove the flag for missing
				sic_arr[ missing ] = new_val
			else:
				print 'error'

		count_missing = ( count_missing[1], len( arr[ arr == 1 ] ) )
		return fill_mask_mismatch( sic_arr, arr, count_missing )
