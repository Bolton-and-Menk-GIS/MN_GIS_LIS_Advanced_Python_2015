import requests
import json
import arcpy
import os
import sys
arcpy.env.overwriteOutput = True

def Message(msg):
    print str(msg)
    arcpy.AddMessage(str(msg))
    return msg

def assertJsonSuccess(data):
    import json
    obj = json.loads(data)
    if 'status' in obj and obj['status'] == "error":
        Message("Error: JSON object returns an error. " + str(obj))
        return False
    else:
        return True
    
def geocode_addresses(new_fc, addresses=[]):
    import json
    import requests
    """Geocodes a list of addresses using the Esri World Geocode Service and returns a
    point feature class

    Quick and dirty geocode.  There is a limit on how many addresses can be
    used before the server rejects the requests (maybe 500?)

    Required:
    new_fc -- new point feature class for geocoded addresses
    addresses -- dictionary of address and feature name {'address' : 'feature description',..}
                 or a list of addresses ['address, city, state, zip'...]
    
    Addresses can be in one of the below formats. 

    # example: pass addresses with description as dictionary
    addresses = {"400 N 1st Ave W, Hartley, IA, 51346" : "Prins Laundromat",
                 "120 S 8th Ave W, Hartley, IA, 51346" : "Hengeveld Construction",
                 "173 S Central Ave, Hartley, IA, 51346" : "Legal Eyes"}
                
    # example: pass addresses in as a list
    addresses = ["901 N Broadway, Saint Louis, Missouri, 63102",
                 "10701 Lambert International Blvd, Saint Louis,
                 "15193 Olive Blvd, Chesterfield, Missouri, 63017"]
    """
    # check to see if addresses are provided as dict
    hasFeature = True
    if not isinstance(addresses, dict):
        addresses = dict((a, '') for a in addresses)
        hasFeature = False
        
    # version info
    # sets projection to WGS 1984 GCS
    prj = 4326
    
    # dictionary to store addresses and points
    addr = {}
    bad = []
    serviceURL = u'http://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/find'
    for address, name in addresses.iteritems():
        # This request only needs the single line address as text and the response formatting parameter .
        params = {'text': address, 'f': 'json'}
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        
        # Connect to service to get its current JSON definition.
        r = requests.post(serviceURL, params=params, headers=headers)
        if (r.status_code != 200):
            Message("Could not geocode address {0}.\r\nhttp status code {1}.".format(address, r.status_code))
            bad.append(address)
        else:
            if not assertJsonSuccess(r.text):
                Message('Error when reading service information:  {0}'.format(r.text))
                bad.append(address)
            
            #Get the first returned location
            loc = False
            candidates = r.json()
            if 'locations' in candidates:
                if candidates['locations']:
                    loc = True
                    candidate = candidates['locations'][0]
                    geo = candidate['feature']['geometry']
                    
                    # Create (X,Y) tuple and Point objects and score
                    pt = (geo['x'], geo['y'])
                    score = candidate['feature']['attributes']['Score']
                    addr[(address, name)] = (arcpy.PointGeometry(arcpy.Point(*pt), prj), score)
            if not loc:
                Message("Could not geocode address \"{0}\"".format(address))

    # create new feature class
    f_length = min([max(len(a) for a in addresses), 255])
    if arcpy.Exists(new_fc):
        arcpy.Delete_management(new_fc)
    arcpy.CreateFeatureclass_management(os.path.dirname(new_fc),
                                        os.path.basename(new_fc),
                                        'POINT', spatial_reference=prj)
    arcpy.AddField_management(new_fc, 'Address', 'TEXT', field_length=f_length)
    arcpy.AddField_management(new_fc, 'Feature', 'TEXT', field_length=100)
    arcpy.AddField_management(new_fc, 'Score', 'SHORT')
     
    # insert rows 
    with arcpy.da.InsertCursor(new_fc, ['SHAPE@', 'Address', 'Feature', 'Score']) as rows:
        for attributes, pt in addr.iteritems():
            add, name = attributes
            xy, score = pt
            rows.insertRow([xy, add, name, score])
            Message('Geocoded address: {0}'.format(add))
        

    # Delete feature field if no feature names supplied
    if not hasFeature:
        arcpy.DeleteField_management(new_fc, ['Feature'])

    # if bad records
    if bad:
        date = time.strftime('_%m_%d_%Y')
        txt = r'C:\Users\{0}\Desktop\Geocode_fail_{1}.txt'.format(os.environ['USERNAME'], date)
        with open(txt, 'w') as f:
            f.writelines('\n'.join(bad))
        os.startfile(txt)
    return new_fc

if __name__ == '__main__':

    # get dictionary of addresses and feature names
    txt = r'.\Hartley.txt'
    with open(txt, 'r') as f:
        addr_info = dict((line.strip().split('|')) for line in f.readlines())

    # output fc
    PATH = os.path.abspath(os.path.dirname(os.path.dirname(sys.argv[0])))
    fc = os.path.join(PATH, 'sample_outputs', 'Hartley_Addresses.shp')

    # run it
    geocode_addresses(fc, addr_info)

##    # geocode my apartment and work
##    fc2 = r'.\geocode\mankato_poi.shp'
##    adds2 = {'50 Hilltop Ln Mankato, MN 56001' : 'my apartment',
##             '1960 Premier Dr Mankato, MN 56001' : 'Bolton & Menk, Inc.'}
##
##    geocode_addresses(fc2, adds2)
        
    
