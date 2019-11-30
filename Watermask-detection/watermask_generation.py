import ndwi
import os
import shutil 


#for a given zip product create its bibari geotiff watermask inside the output directory
def calculate_watermask(out_dir, inputproductpath):
	
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)
	data_temp_dir =	 os.path.join(out_dir, 'data_temp')
	if not os.path.exists(data_temp_dir):
		os.makedirs(data_temp_dir)
		
	file_name_no_ext = os.path.basename(os.path.splitext(inputproductpath)[0])	
	generated_watermask_tif = os.path.join(out_dir, file_name_no_ext + '_water_bodies.tif')
	
	ndwi.createS2Watermask(data_temp_dir, inputproductpath, generated_watermask_tif)
	
	json_file = os.path.join(out_dir, 'output_summary_s2.json')

	shutil.rmtree(data_temp_dir)
	print("Intermediate files have been removed.")
	
	return generated_watermask_tif


#sample execution	
#output_dir = "results_s2"
#in_path = 'S2A_MSIL1C_20191122T155551_N0208_R054_T18TUN_20191122T190954.zip'
#calculate_watermask(output_dir, in_path)