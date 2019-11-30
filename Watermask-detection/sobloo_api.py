import requests, sys, time
import datetime

#import urllib3
#urllib3.disable_warnings()

#The key is required to download files wit
APIKEY_SECRET = 'PvCXI3K3qs6Gb7_mUbHlzcJc3rs53g-UeYsc2TxDdunRmr2aqhT4zvwDuEzNU6eJ1Nx9wWKvRCfEV1JKrET3wQ=='


def callAPI(cmd1, auth):
	if (auth == 1):
	# we inject here the SECRET APIKEY from our sobloo account page
		headers={"Authorization":"Apikey " + APIKEY_SECRET}
		r = requests.get(cmd1, headers=headers, verify=False)
	else:
		# this API does not need authentication	 
		r = requests.get(cmd1, verify=False)	 

	if( r.status_code != requests.codes.ok ):			
		print("Error: %s  for the request cmd1 <%s>." % (r.status_code,cmd1))
		return -1		
	else:		   
	# return the response
		return r

def is_empty(any_structure):
	if any_structure:
		return False
	else:
		return True		

#Get product id given the product name
def getInternalId(prodName):
	print("Product name: " + prodName)
	# query to rest search API to get the internal ID of a product through its name
	cmd = "https://sobloo.eu/api/v1/services/search?f=identification.externalId:eq:" + prodName + "&include=previews,identification&pretty=true"
	# this API does not need authentication
	r = requests.get(cmd, verify=False)
	if( r.status_code != requests.codes.ok ):
		print("Error: %s  for the request cmd <%s>." % (r.status_code,cmd))
		internalId = -1
	else:
		# the returned json object contains the internal Id (only one product returned)
		#print(r.json())
		j = r.json()
	if j["totalnb"] == 0:
		print("No matching products found")
		internalId = -1
	else:
		internalId = j['hits'][0]['data']['uid']
		return internalId
	
#Download a product given the product id	
def downloadProd(prodName, download_filepath):
	# Get product internal Id
	iid = getInternalId(prodName)
	print("Product id: " + str(iid))
	if (iid == -1):
		print("Product %s not found" % (prodName))
		return -1
	# once we get the internal ID of the product we can start downloading it through the API
	# note the APIKEY injection in the headers to authenticate
	cmd = "https://sobloo.eu/api/v1/services/download/" + str(iid)
	# we inject here the APIKEY got from our account page
	headers={"Authorization":"Apikey " + APIKEY_SECRET}
	print("## Sending downloading request..")
	r = requests.get(cmd, headers=headers, verify=False)
	print("Teleiwse to request")
	if( r.status_code != requests.codes.ok ):
		print("Error: %s  for the request cmd <%s>." % (r.status_code,cmd))
		return -1
	else:
		# Write the data in the current directory
		#filename = os.path.join(downloaded_products_dir, prodName + ".zip")
		print("Anoigei gia grapsimo:")
		with open(download_filepath, "w+b") as f:
			f.write(r.content)
		return 0
  

#Prints AND returns the the filenames of the detected products
def printProductDetail(jsonObject):
	
	products_list = []
	
	# Display the results
	print("ksekinaw ta details")
	if is_empty(jsonObject):
		print("The object to be printed is empty.")
		return -1

	for elements in jsonObject["hits"]:
		uid="empty"
		try:
			uid = elements["data"]["uid"]
			ident=elements["data"]["identification"]
			acq = elements["data"]["acquisition"]
			prodName= elements["data"]["identification"]["externalId"]
			prodType=elements["data"]["identification"]["type"]
			prodLevel=elements["data"]["production"]["levelCode"]
			geoname= elements["data"]["enrichment"]["geonames"]
			orbit=elements["data"]["orbit"]
			#archive = sizeMB = elements["data"]["archive"]
			#print(archive)
			#sizeMB = elements["data"]["archive"]["size"]
			location=elements["data"]["spatialCoverage"]["geometry"]["centerPoint"]
			print("uid: %s name: %s acq: %s" % (uid,prodName,datetime.datetime.fromtimestamp(acq["centerViewingDate"]/1000)))
			products_list.append(prodName)
			
		except:
			print("Unexpected exception %s while rendering object with uid: %s ." % (sys.exc_info()[0],uid))
	
	return products_list
		  


#list products of a given city, after a given date-time   
def listProductGeoname(typeGeo,thegeoname, starting_date_str):

	date_time_obj = datetime.datetime.strptime(starting_date_str, '%Y-%m-%d %H:%M:%S')
	starting_ts = datetime.datetime.timestamp(date_time_obj)*1000
	
	all_products = []
	
	# Careful the search query does not allow going beyond the 10000th element
	# So a query such as &&from=9999&&size=2 ends with an HTTP 500 error, same for &&from=10000&&size=1
	if (typeGeo == "country"):
		filter = "enrichment.geonames.name"
	elif (typeGeo == "states"):
		filter = "enrichment.geonames.states.name"
	elif (typeGeo == "county"):
		filter = "enrichment.geonames.states.counties.name"
	elif (typeGeo == "city"):
		filter = "enrichment.geonames.states.counties.cities.name"
	elif (typeGeo == "village"):
		filter = "enrichment.geonames.states.counties.villages.name"
	else:
		filter = "all"
	

	offset = 0
	nbReturn=1000
	# Make a first call to retrieve how many elements will be returned
	#cmd = "https://sobloo.eu/api/v1/services/search?f=" + filter + ":like:" + thegeoname +"&&size=" + str(nbReturn)
	cmd = "https://sobloo.eu/api/v1/services/search?f=" + filter + ":like:" + thegeoname + "&f=acquisition.centerViewingDate:gte:%s" % starting_ts  + "&&size=" + str(nbReturn)
	
	ret = callAPI(cmd,0)
	print("perase apo edw")
	
	if (ret != -1):
		try:
			nbHits=ret.json()["totalnb"]
			print("nbElements returned: %s" % nbHits)
			if (nbHits == 0):
				print("No hits !")
				return
			# Iterate the query by steps of nbReturn elements to display them all
			if (nbHits > nbReturn):
				nbCalls=int((nbHits/nbReturn))
				for i in range(0,nbCalls):
					print("mphke edw")
					#"&&f=state.services.download:eq:internal"
					#cmd = "https://sobloo.eu/api/v1/services/search?f=" + filter + ":like:" + thegeoname + "&&from=" + str(i*nbReturn) + "&&size=" + str(nbReturn)
					cmd = "https://sobloo.eu/api/v1/services/search?f=" + filter + ":like:" + thegeoname + "&f=acquisition.centerViewingDate:gte:%s" % starting_ts+  "&&from=" + str(i*nbReturn) + "&&size=" + str(nbReturn)
					
					
					ret2 = callAPI(cmd,0)
					print("Phre ta apotelesmata")
					res = printProductDetail(ret2.json())
					
					all_products = all_products + res
			else:
				res = printProductDetail(ret.json())
				all_products = all_products + res
		except:
			print("Unexpected exception %s" % (sys.exc_info()[0]))	 

		return all_products
	else:
		print("No elements returned")