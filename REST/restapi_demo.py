import restapi
import os
import sys
arcpy.env.overwriteOutput = True

# temp directory
_dir = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'sample_outputs')

# emerald ash borer detection url
eab_url = 'http://gis.mda.state.mn.us/ArcGIS/rest/services/MN_Agriculture_EAB_Detection/MapServer'
eab = restapi.MapService(eab_url)

# list layers
print eab.list_layers()

# make layer for standing infested trees
trees = eab.layer('standing infested trees')

# run search cursor through feature layer
fields = ['SHAPE@', 'OwnerName', 'Latitude', 'Longitude', 'Check_Date', 'Zone']
cursor = trees.cursor(fields)
for row in cursor:
    print row

print '\n' * 3

# loop through layers and export to feature class
for layer in eab.list_layers():
    out = os.path.join(_dir, layer.replace(' ', '_') + '.shp')
    eab.layer_to_fc(layer, out)
    

