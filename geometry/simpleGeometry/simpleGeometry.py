import arcpy
import os
import sys
arcpy.env.overwriteOutput = True

pt1 = arcpy.Point(3,5)
pt2 = arcpy.Point(3,8)
pt3 = arcpy.Point (0,8)
pt4 = arcpy.Point(0,5)

# make square
box = arcpy.Polygon(arcpy.Array([pt1, pt2, pt3, pt4]), 103734)
# can explicitly close box by adding pt1 as last point

# get perimeter and area (12 and 9)
print 'Perimiter and area of box'
print box.length, box.area, '\n' # do we have tolerance issues?

# get centroid
centroid = box.centroid

print 'Box contains centroid: {}'.format(box.contains(centroid))

# get center distance to corner
print '\nDistance from centroid to corner is: {}'.format(arcpy.PointGeometry(centroid).distanceTo(pt1))

# check for same geometry
print '\nPoint 1 (3, 5) equals Point 2 (3, 5):'
print pt1.equals(arcpy.Point(3, 5)), '\n'

# print coordinates
print '\nPoint 1 coordinates:'
print pt1.X, pt1.Y

# make polyline from box boundary
print '\nMade polyline from box boundary, length is:'
line = box.boundary()
print line.length

# construct line manually
line2 = arcpy.Polyline(arcpy.Array([pt1, pt2, pt3, pt4, pt1]), 103734) # added pt1 at end to close it
print '\nLine length equals manually constructed polyline: {}'.format(line.equals(line2))

# make a polygon with a donut hole
buff = box.buffer(5)
donut = buff.difference(box)

# can copy to in_memory
features = arcpy.management.CopyFeatures([box, donut], r'in_memory\temp_polys')

print '\n'
# --------------------------------------------------------------------------------------#
# reading geometries
data = os.path.join(os.path.dirname(os.path.abspath(os.path.dirname(sys.argv[0]))), 'DATA')
polys = os.path.join(data, 'Polygons.shp')
lines = os.path.join(data, 'Lines.shp')
multi = os.path.join(data, 'Multipoint.shp')

# read through polys (pretty much a copy of esri's help docs)
print 'Checking polygons...\n'
with arcpy.da.SearchCursor(polys, ['SHAPE@', 'PType', 'OID@']) as rows:
    for row in rows:
        print 'Feature: {}'.format(row[2])
        print 'Type: {}'.format(row[1])

        # loop thru parts
        p = 0
        for part in row[0]:
            print 'Part: {}'.format(p)

            # loop thru points in part
            for i, pnt in enumerate(part):
                if pnt:
                    print '{0}: X: {1}, Y: {2}'.format(i, pnt.X, pnt.Y)
                else:
                    # donut holes are null or None
                    print 'donut hole:'
            p += 1
        print '\n'

# read through lines
print 'Checking lines...\n'
with arcpy.da.SearchCursor(lines, ['SHAPE@', 'PType', 'OID@']) as rows:
    for row in rows:
        print 'Feature: {}'.format(row[2])
        print 'Type: {}'.format(row[1])

        # loop thru parts
        p = 0
        for part in row[0]:
            print 'Part: {}'.format(p)

            # loop thru points in part
            for i, pnt in enumerate(part):
                print '{0}: X: {1}, Y: {2}'.format(i, pnt.X, pnt.Y)

            p += 1
        print '\n'

# read through multipoints
print 'Checking multipoints...\n'
with arcpy.da.SearchCursor(multi, ['SHAPE@', 'OID@']) as rows:
    for row in rows:
        print 'Feature: {}'.format(row[1])

        # loop thru points in part
        for i, pnt in enumerate(row[0]):
            print '{0}: X: {1}, Y: {2}'.format(i, pnt.X, pnt.Y)


