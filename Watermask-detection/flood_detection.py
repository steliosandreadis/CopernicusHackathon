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


def flood_detection(city_name, date_time_str, out_dir):

	found_products = sobloo_api.listProductGeoname('city', city_name, date_time_str)

	print(found_products)

	if len(found_products) > 0:
		for each_product in found_products:
			print(each_product)
			product_path_zip = os.path.join(os.path.join(downloaded_products_dir, each_product + '.zip'))
			
			#check if zip product already downloaded
			if os.path.exists(product_path_zip):
				print('product already downloaded')
			else:
				sobloo_api.downloadProd(each_product, downloaded_products_dir)
			
			if os.path.exists(product_path_zip):	
				watermask_generation.calculate_watermask(output_dir, product_path_zip)

###Sample execution#
city='Venice'
date_time_str = "2019-11-20 00:00:01"
downloaded_products_dir = 'downloaded_products'
output_dir = "results_s2"

flood_detection('Venice', date_time_str, output_dir)