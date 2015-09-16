#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      calebma
#
# Created:     13/04/2015
# Copyright:   (c) calebma 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy
import os
import sys
import math
from datetime import datetime as d
arcpy.env.overwriteOutput = True

def Message(msg):
    print str(msg)
    arcpy.AddMessage(msg)

def findDistance(a,b):
    x = abs(a[0] - b[0])
    y = abs(a[1] - b[1])
    return math.sqrt((x*x) + (y*y))

def nearFarPoints(in_points, near_points, out_table, dist_type=min):
    """function to find the minimum or maximimum distance between points

    Required:
        in_points -- source points for near analysis
        near_points -- points to find distance to (can be same as in_points)
        out_table -- output near table

    Optional:
        dist_type -- set to min or max to find the closest or farthest distnace
            between points.
    """

    # fix args if coming from script tool
    if str(dist_type).lower() == 'max':
        dist_type = max
    else:
        dist_type = min

    startTime = d.now()
    # grab xy coords
    with arcpy.da.SearchCursor(in_points, ['OID@','SHAPE@XY']) as rows:
        point_dict = dict((r[0],r[1]) for r in rows)

    # grab xy coords near points
    with arcpy.da.SearchCursor(near_points, ['OID@','SHAPE@XY']) as rows:
        npoint_dict = dict((r[0],r[1]) for r in rows)


    # create dictionary to find nearest point
    same = in_points == near_points
    near_dict = {}
    for key in point_dict.keys():
        this_pt = point_dict[key]
        distList = {}
        for oid,coords in npoint_dict.iteritems():
            distList[oid] = findDistance(this_pt,coords)
        if same:
            closest = dist_type(filter(None, distList.values()))
        else:
            closest = dist_type(distList.values())
        near_id = [k for k,v in distList.iteritems() if v==closest][0]
        near_dict[key] = [near_id,closest]
    del point_dict, distList

    # create output table
    path, name = os.path.split(out_table)
    if arcpy.Exists(out_table):
        arcpy.management.Delete(out_table)
    arcpy.conversion.TableToTable(in_points,path,name)
    arcpy.management.AddField(out_table,'NEAR_ID','LONG')
    arcpy.management.AddField(out_table,'NEAR_DIST','DOUBLE')
    fields = ['OID@','NEAR_ID','NEAR_DIST']
    with arcpy.da.UpdateCursor(out_table,fields) as rows:
        for row in rows:
            if row[0] in near_dict:
                row[1] = near_dict[row[0]][0]
                row[2] = near_dict[row[0]][1]
                rows.updateRow(row)
    Message('Created: %s' %os.path.basename(out_table))
    Message('(Elapsed time: %s)' %(str(d.now() - startTime)[:-3]))
    return out_table

if __name__ == '__main__':

    # Run it
    nearFarPoints(*tuple(arcpy.GetParameterAsText(i) for i in range(arcpy.GetArgumentCount())))
