import gdal
import numpy as np
import cv2

#Crates a transparent PNG image, depicting the water bodies, based on the previously generated watermask
#input: the path of the watermask geotiff file, the path of the output png file (must be string), the max edge size in pixels (e.g. 1000 pixels)
#output: a PNG file with transparent the non-water areas and with a customn color for the water ones (e.g. red or green).

def createTransparentS2Watermask(input_watermask_tif, output_watermask_png, max_edge_pixel_size):

	#load watermask band in a numpy array
	ds = gdal.Open(input_watermask_tif)
	mask_array = np.array(ds.GetRasterBand(1).ReadAsArray())

	#scl image imensions
	initial_y = mask_array.shape[0]
	initial_x = mask_array.shape[1]




	#find image scale using the max resolution (x or y?)
	if initial_y >= initial_x:
		imgScale = float(max_edge_pixel_size)/initial_y
		newY = max_edge_pixel_size
		newX =  int(round(initial_x*imgScale))

	else:
		imgScale = float(max_edge_pixel_size)/initial_x
		newX = max_edge_pixel_size
		newY =  int(round(initial_y*imgScale))

	resized_watermask = cv2.resize(mask_array, dsize=(newX, newY), interpolation=cv2.INTER_NEAREST)
	
	#Green bright: 51,255,51
	my_3d_array_bgr=np.zeros((newY,newX,3))
	my_3d_array_bgr[resized_watermask == 1] = (246,206,45) #51,255,51


	#Create trasnpsarency layer
	alpha_array = np.full((newY, newX), 255)
	my_3d_array_bgr_alpha = np.dstack( ( my_3d_array_bgr, alpha_array))
	#mark the pixels with value 255,255,255 that are now visible i.e. alpha is 255 as transparent, i.e. new alpha 0
	my_3d_array_bgr_alpha[resized_watermask == 0] = (255, 255, 255, 0)

	cv2.imwrite(output_watermask_png, my_3d_array_bgr_alpha)

	return 'success'
