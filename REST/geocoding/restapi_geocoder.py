import restapi
import sys
import os
import arcpy
arcpy.env.overwriteOutput = True

adds = ['425 PORTLAND AVE S, MINNEAPOLIS, MN 55488',
        '233 5TH AVE S, MINNEAPOLIS, MN 55415',
        '1000 HAWTHORNE AVE, MINNEAPOLIS, MN 55403',
        '551 10TH ST S, MINNEAPOLIS, MN 55404',
        '1225 LASALLE AVE, MINNEAPOLIS, MN 55403',
        '517 HENNEPIN AVE, MINNEAPOLIS, MN 55403']

url = 'http://gis.hennepin.us/arcgis/rest/services/Locators/HC_COMPOSITE/GeocodeServer'
geocoder = restapi.Geocoder(url)

# geocode addresses using SingleLine field
singleLine_results = geocoder.geocodeAddresses(adds, outSR=103734)

# geocode using recs parameter (record set)
# format example:
# recs = {'records':
#           [
#             {'attributes':
#               {'Street': '425 PORTLAND AVE S',
#                'City': 'MINNEAPOLIS',
#                'ZIP': '55488'}
#             }
#           [
#        }
records = {'records': []}
for addr in adds:
    records['records'].append({'attributes':
                                   {'Street': addr.split(',')[0],
                                   'City': addr.split(',')[1],
                                   'ZIP': addr.split()[-1]}})
    
recs_results = geocoder.geocodeAddresses(records, outSR=103734)

# report results and export
ave_sl = sum([r.score for r in singleLine_results.results]) / float(len(singleLine_results))
ave_rec = sum([r.score for r in recs_results.results]) / float(len(recs_results))
print 'Number of results from singleLineField search: {}, average score: {}'.format(len(singleLine_results), ave_sl)
print 'Number of results from record set search: {}, average score: {}\n'.format(len(recs_results), ave_rec)

# export results
_dir = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(sys.argv[0]))), 'sample_outputs')
sl = os.path.join(_dir, 'singleLineField_results.shp')
rec = os.path.join(_dir, 'recordSet_results.shp')

# must pass in geocode result object
geocoder.exportResults(singleLine_results, sl)
geocoder.exportResults(recs_results, rec)
