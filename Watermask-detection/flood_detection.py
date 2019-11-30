'''
This fuunction discovers the most recent Sentinel-2 products for a city, downloads them. Sobloo API is used.
Input:
-City name
-Date after which the products will be download
output: The downloaded zip products
'''

import sobloo_api
import datetime
import os

import watermask_generation


def flood_detection(city_name, date_time_str, base_download_dir, results_dir):

	downloaded_products_dir = os.path.join(base_download_dir, city)
	output_dir = os.path.join(results_dir, city)
	
	#create dirs if not exits
	if not os.path.exists(base_download_dir):
		os.makedirs(base_download_dir)

	if not os.path.exists(downloaded_products_dir):
		os.makedirs(downloaded_products_dir)
		
		
	if not os.path.exists(results_dir):
		os.makedirs(results_dir)

	if not os.path.exists(output_dir):
		os.makedirs(output_dir)	

	found_products = sobloo_api.listProductGeoname('city', city_name, date_time_str)
	print("edw")
	print(found_products)

	if found_products and len(found_products) > 0:
		for each_product in found_products:
			print(each_product)
			product_path_zip = os.path.join(os.path.join(downloaded_products_dir, each_product + '.zip'))
			
			#check if zip product already downloaded
			if os.path.exists(product_path_zip):
				print('product already downloaded')
			else:
				sobloo_api.downloadProd(each_product, product_path_zip)
			
			if os.path.exists(product_path_zip):	
				watermask_generation.calculate_watermask(output_dir, product_path_zip)
	else:
		print("No recent products for selected city")

###Sample execution#
city='Paris'
date_time_str = "2019-11-20 00:00:01"

base_dl_dir = 'downloaded_products'
res_dir = "results_s2"

flood_detection(city, date_time_str, base_dl_dir, res_dir)