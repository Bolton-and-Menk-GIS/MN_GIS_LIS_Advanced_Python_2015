import os
import sys
import arcpy
import requests
import urllib
arcpy.env.overwriteOutput = True

# simple request
# get illinois counties query

# rest endpoint
url = 'http://ags10.dot.illinois.gov/ArcGIS/rest/services/DataSharing/ClipAndShip3Map/MapServer/57/query?'
params = {'where':'1=1', 'f':'pjson', 'outFields':'*'}

# get county names by requests.post()
r = requests.post(url, params).json() # get results back as json

# print all county names
print sorted([feat['attributes']['COUNTY_NAM'] for feat in r['features']])

# the lazy way, load to a feature set
query_url = url + urllib.urlencode(params)
print '\n\n' + query_url

# load http results to feature set
fs = arcpy.FeatureSet()
fs.load(query_url) # can feed in the url, the load() method is smart enough to process the results

# copy features to shapefile
_dir = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'sample_outputs')
out_shp = os.path.join(_dir, 'IL_Counties.shp')
arcpy.management.CopyFeatures(fs, out_shp)
print '\ncreated: "{}"'.format(out_shp)

# amtrak station url
station_url = 'http://ags10.dot.illinois.gov/ArcGIS/rest/services/MapBase/amtrak/MapServer/0/query?'

# grab the Amatrak station from my home town
params = {'where': "City = 'Macomb'", 'f': 'pjson', 'outFields': '*'}
amtrk_query_url = station_url + urllib.urlencode(params)

# output shapefile
mac = os.path.join(_dir, 'Macomb_Station.shp')
fs = arcpy.FeatureSet()
fs.load(amtrk_query_url)
arcpy.management.CopyFeatures(fs, mac)
print '\ncreated: "{}"'.format(mac)
