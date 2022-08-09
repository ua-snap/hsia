import numpy as np
import rasterio, os, glob

class SeaIceRaw( object ):
	def __init__( self, fn ):
		'''
		simplify some ugliness with working with NSIDC 0051
		flat binary files.  This works for the current implementation
		(v1.1) of the flat binary grids for the NSIDC Sea Ice Concentration
		Grids (0051)

		metadata: https://nsidc.org/data/docs/daac/nsidc0051_gsfc_seaice.gd.htm

		Arguments:
		----------
		fn = [str] filename of .bin file to work with

		'''
		self.fn = fn
		self.header = self._read_header()
		self.height = self.header[ 'rows' ] # 448
		self.width = self.header[ 'cols' ] # 304
		# below hardwired. parsed from metadata document
		self.crs = '+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 +k=1 +x_0=0 +y_0=0 +a=6378273 +b=6356889.449 +units=m +no_defs'
		self.geotransform = (-3850000.0, 25000.0 ,0.0, 5850000.0, 0.0, -25000.0)
		self.nodata = None
		self.scaling_factor = self.header[ 'scaling_factor' ]

	def get_metadata( self ):
		'''
		return a rasterio-style metadata dict for the output file to be 
		created.  Only GeoTiff is currently supported.
		'''
		from affine import Affine as A
		meta = {'transform': A.from_gdal( *self.geotransform ),
				'count': 1,
				'crs': self.crs,
				'driver': u'GTiff',
				'dtype': 'uint8',
				'height': self.height,
				'nodata': self.nodata,
				'width': self.width,
				'compress': 'lzw'}
		return meta
	def _read_header( self ):
		'''
		[HIDDEN] function to read the flat binary header file from the NSIDC 0051 file type
		This is very specific to this filename type and will most likely not work for others.

		The hardwired lists of keys and types is generated by hand prior to writing this function
		(hacky!) from this metadata document and particularly table 1, though all the tables are
		quite useful.  

		METADATA (working as of May 2016): https://nsidc.org/data/docs/daac/nsidc0051_gsfc_seaice.gd.htm

		'''
		import struct
		with open( self.fn, "rb" ) as f:
			header1 = f.read( 126 )
			header2 = f.read( 24 )
			header3 = f.read( 80 )
			header4 = f.read( 70 )
		
		# convert header1 to dict of useful parts	
		header1_keys = [ 'nodata', 'cols', 'rows', 'unused_1', 'lat_ext', 'greenwich_orient', 'unused_2', \
						'j_coord', 'i_coord', 'instrument', 'data_descriptor', 'julian_start', 'hour_start', \
						'minute_start', 'julian_end', 'hour_end', 'minute_end', 'year', 'julian_day', \
						'channel', 'scaling_factor' ]
		header1_converter = [int, int, int, str, float, float, float, float, float, str, str, str, int, int, \
							int, int, int, int, int, int, int]
		slices = [(arr.min(), arr.max()) for arr in np.split( np.array( range(126) ), len(header1_keys) )]
		unpacked = [ struct.unpack( '5s', header1[i:j] )[0] for i,j in slices ]
		unpacked_converted = [ i(j) for i,j in zip(header1_converter, unpacked)]
		return  dict( zip( header1_keys, unpacked_converted ) )
	def open( self ):
		'''
		open a flat binary file from the NSIDC_0051 Monthly Dataset and 
		make it numpy array.

		# information current as of April 9th, 2015
		Data Set Name : Sea Ice Concentrations from Nimbus-7 SMMR and DMSP SSM/I-SSMIS Passive Microwave Data
		Data Set Website: http://nsidc.org/data/nsidc-0051
		Data FTP : ftp://sidads.colorado.edu/pub/DATASETS/nsidc0051_gsfc_nasateam_seaice/final-gsfc/north/monthly/

		function inspired by: https://github.com/npolar/RemoteSensing/blob/master/IcePersistency/IcePersistency.py

		'''
		import rasterio
		import numpy as np

		with open( self.fn, 'rb' ) as f:
			f.seek( 300 )
			arr = np.fromfile( f, dtype=np.uint8 ).reshape( self.height, self.width )
			# scale it: based on a 250 scaling factor
			arr[ arr <= 250 ] = arr[ arr <= 250 ] / 2.5
		return arr
	def _to_gtiff( self, output_filename=None ):
		'''
		write raw the nsidc-0051 dataset as a GeoTiff in 
		native extent, resolution, CRS, etc.

		Arguments:
		----------
		output_filename = [str] (optional) path to the file to create.

		Returns:
		--------
		output_filename of the newly generated GeoTiff

		'''
		from rasterio.warp import Resampling, reproject
		
		arr = self.open()
		meta = self.get_metadata()

		if not output_filename:
			output_filename = self.fn.replace( '.bin', '.tif' )
		with rasterio.open( output_filename, 'w', **meta ) as out:
			out.write( arr, 1 )
		return output_filename
	def to_gtiff_3413( self, output_filename=None ):
		if output_filename:
			# hack to get a filename arg in this function 
			fn = self._to_gtiff( output_filename=output_filename )
		else:
			fn = self._to_gtiff()
		
		output_filename = fn.replace( '.tif', '_3413.tif')
		os.system( 'gdalwarp -overwrite -q -multi -t_srs EPSG:3413 ' + fn + ' ' + output_filename )
		return output_filename
	def to_gtiff_3572( self, output_filename=None ):
		fn = self._to_gtiff()
		
		os.system( 'gdalwarp -overwrite -q -multi -t_srs EPSG:3572 -te_srs EPSG:3572 -dstnodata 120 -te -4862550.515 -4894840.007 4870398.248 4889334.803 -tr 17075.348707767432643 -17075.348707767432643 ' + fn + ' ' + output_filename )
		return output_filename


class TemplateRaster( object ):
	def __init__( self, fn ):
		'''
		methods to simplify working with 
		a template raster file from a previous 
		version of the HSIA, which allows for 
		ease of use when generating new data to
		the same standard.

		Arguments:
		----------
		fn = [str] path to the file used as a template 
			for the processing into HSIA format.

		'''
		import rasterio
		self.fn = fn
		self.rst = rasterio.open( self.fn )
		self.meta = self.rst.meta

	def get_mask( self ):
		''' 
		return landmask - works 
		only for this simple purpose
		'''
		arr = self.rst.read( 2 )
		arr[ arr > 0 ] = 2
		arr[ arr == 0 ] = 1
		arr[ arr == 2 ] = 0
		return arr
