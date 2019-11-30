import os
import gdal
import numpy as np
import zipfile
import shutil
import custom_color_mask

import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling


'''
Uses Sentinel-2 product to create a binary watermask based on MNDWI water index. Threshold was manually set to zero.
Inputs:
-Sentiel-2 zip product
-
'''



###discards the extension of the provided path and returns the rest
def filename_discard_extension(full_path_filename):
	return os.path.splitext(full_path_filename)[0]

#saves greyscale tif from 2d array, will be used for watermask creation
def save_geo_tiff(gdal_guidance_image, output_file, out_format, rasterXSize, rasterYSize, array_image, dtype, noDataValue = ""):
	geoTrans_guidance = gdal_guidance_image.GetGeoTransform() # Retrieve Geo-information of guidance image and save it in geoTrans_guidance
	wkt_guidance = gdal_guidance_image.GetProjection() # Retrieve projection system of guidance image into well known text (WKT) format and save it in wkt_guidance
	  
	#format = 'GTiff'
	driver= gdal.GetDriverByName(out_format) #Generate an object of type GeoTIFF / KEA 
	dst_ds = driver.Create(output_file, rasterXSize, rasterYSize, 1, dtype, options = [ 'COMPRESS=DEFLATE' ])
	#Create a raster of type Geotiff / KEA with dimension Guided_Image.RasterXSize x Guided_Image.RasterYSize, with one band and datatype of GDT_Float32
	#LZW or DEFLATE compression
	if dst_ds is None: #Check if output_file can be saved
		print ("Could not save output file %s, path does not exist." % output_file)
		quit()
		#sys.exit(4)
	   
	dst_ds.SetGeoTransform(geoTrans_guidance) # Set the Geo-information of the output file the same as the one of the guidance image
	dst_ds.SetProjection (wkt_guidance)
	if noDataValue !="":
		dst_ds.GetRasterBand(1).SetNoDataValue(noDataValue)
		print("Value to be replaced with NaN was given: "+ str(noDataValue))
	dst_ds.GetRasterBand(1).WriteArray(array_image) # Save the raster into the output file 
	dst_ds.FlushCache()	 # Write to disk.


def warp2WGS84(in_raster, out_raster):

	dst_crs = 'EPSG:4326'

	with rasterio.open(in_raster) as src:
		transform, width, height = calculate_default_transform(
			src.crs, dst_crs, src.width, src.height, *src.bounds)
		kwargs = src.meta.copy()
		kwargs.update({
			'crs': dst_crs,
			'transform': transform,
			'width': width,
			'height': height,
			"compress": "LZW"
		})

		with rasterio.open(out_raster, 'w', **kwargs) as dst:
			for i in range(1, src.count + 1):
				reproject(
					source=rasterio.band(src, i),
					destination=rasterio.band(dst, i),
					src_transform=src.transform,
					src_crs=src.crs,
					dst_transform=transform,
					dst_crs=dst_crs,
					resampling=Resampling.nearest)
	

#input: the path of the input .jp2 file (must be string), the path of the output png file (must be string), the size in pixels of the biggest edge of the output image (must be integer)
#Output: a watermask in geotif format

def createS2Watermask(data_temp_dir, input_product, watermask_filename_tif):
	
	directory_to_extract_to = os.path.join(data_temp_dir, 'extracted')
	
	bands_to_keep = [("B03", "B03.jp2"), ("TCI","TCI.jp2"), ("B11","B11.jp2")]
	
	files_bands = {}

	print(os.path.isfile(input_product))
	my_zip = zipfile.ZipFile(input_product) # Specify your zip file's name here
	for each_file in my_zip.namelist():
		for each_desired_band in bands_to_keep:
			if my_zip.getinfo(each_file).filename.endswith(each_desired_band[1]):
				my_zip.extract(each_file, directory_to_extract_to) # extract the file to current folder if it is a text file
				files_bands[each_desired_band[0]] = os.path.join(directory_to_extract_to, each_file)

	
	green = files_bands['B03']
	swir = files_bands['B11']
	tci = files_bands['TCI']

	#green_path_no_ext = filename_discard_extension(green)
	swir_path_no_ext = filename_discard_extension(swir)
	
	sharpen = 'gdalwarp -overwrite -tr 10 -10 %s %s_sharpened.tif -r near' %(swir, swir_path_no_ext)
	os.system(sharpen)
	
	#load bands in a numpy arrays	
		
	ds_green = gdal.Open(green) #Your data the one you want to clip
	srcband = ds_green.GetRasterBand(1)
	green_array = srcband.ReadAsArray(0, 0, ds_green.RasterXSize, ds_green.RasterYSize).astype(np.float)
	
	ds_swir = gdal.Open(swir_path_no_ext + '_sharpened.tif') #Your data the one you want to clip
	srcband = ds_swir.GetRasterBand(1)
	swir_array = srcband.ReadAsArray(0, 0, ds_swir.RasterXSize, ds_swir.RasterYSize).astype(np.float)

	#calculate mndwi (allow div by zero)
	np.seterr(divide='ignore', invalid='ignore')
	mndwi = (green_array - swir_array) / (green_array + swir_array)
			
	#Create a mask with 1 for water, 0 for non-water
	mndwi[mndwi > 0.0] = 1
	mndwi[mndwi <= 0.0] = 0	
	
	save_geo_tiff(ds_green, watermask_filename_tif, 'GTiff', ds_green.RasterXSize, ds_green.RasterYSize, mndwi, gdal.GDT_Byte)

	out_water_temp_png = os.path.join(data_temp_dir, 'watermask_full.png')
	#this is the 1000px png watermask
	out_water_png = os.path.splitext(watermask_filename_tif)[0] + '_small.png'	

	#generate the small watermask png file
	#convert_to_png_cmd = 'gdal_translate -of PNG -scale 0 1 0 255 %s %s' % (watermask_filename_tif, out_water_temp_png)		
	#os.system(convert_to_png_cmd)
		
	#convert_to_png_cmd = 'gdal_translate -of PNG -outsize 1000 -scale %s %s' % (out_water_temp_png, out_water_png)		
	#os.system(convert_to_png_cmd)
	
	###Warp the image
	warped_mask_tif = os.path.splitext(watermask_filename_tif)[0] + '_warped.tif'
	warp2WGS84(watermask_filename_tif, warped_mask_tif)
	
	###create transparent png of the warped image
	custom_color_mask.createTransparentS2Watermask(warped_mask_tif, out_water_png, 1000)
	
	###write coordinates and epsg of warped file
	with rasterio.open(warped_mask_tif) as src:
		coords_txt_file = os.path.splitext(watermask_filename_tif)[0] + '_warped_crs.txt'
		file_crs = open(coords_txt_file,"w")
		file_crs.write("\n")
		file_crs.write(str(src.crs))
		file_crs.write(str(src.bounds))
		file_crs.close()

	#actually just the tci
	out_water_tci = os.path.splitext(watermask_filename_tif)[0] + '_tci.png'
	convert_to_png_cmd = 'gdal_translate -of PNG -outsize 1000 -scale %s %s' % (tci, out_water_tci)		
	os.system(convert_to_png_cmd)

