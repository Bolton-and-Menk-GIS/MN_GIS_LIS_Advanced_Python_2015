import arcpy
arcpy.env.addOutputsToMap = True

# for use in ArcMap
x,y = 541088, 167645
sr = arcpy.SpatialReference(103734) #Hennepin county coordinates

# create point and display in ArcMap
pt = arcpy.PointGeometry(arcpy.Point(x, y), sr)
arcpy.management.CopyFeatures(pt, r'in_memory\temp_pt')

# write polygons
# make donut hole
buff50 = pt.buffer(50)
buff00 = pt.buffer(100)

arcpy.management.CopyFeatures(buff100.difference(buff50), r'in_memory\donut')

# manually create polygon with donut hole (2 parts)
coords = [
         [[541090, 167645],
         [541090, 167695],
         [541140, 167695],
         [541140, 167645]],
         None,
         [[541100, 167655],
         [541130, 167655],
         [541130, 167685],
         [541100, 167685]]
        ]

# create array and polygon
ar = arcpy.Array()
for part in coords:
    ar.add(arcpy.Array(arcpy.Point(*c) for c in part)) if part else ar.add(arcpy.Array())
poly = arcpy.Polygon(ar, sr) 
arcpy.management.CopyFeatures(poly, r'in_memory\temp')

# line methods
# create 100 yard line on football field, then break into 10 groups
start = (540938, 167565)
end = (start[0] + 300, start[1])
line = arcpy.Polyline(arcpy.Array(arcpy.Point(*c) for c in [start, end]), sr)
tenYrdArray = []
lstart = 0
for i in range(1,11):
    tenYrdArray.append(arcpy.Polyline(
                    arcpy.Array([line.positionAlongLine(lstart).centroid,
                                line.positionAlongLine(i*0.1, True).centroid]), sr)) # must use centroid to get point object, otherwise is PointGeometry
    lstart = (i * 0.1) * line.length

tenYards = arcpy.management.CopyFeatures(tenYrdArray, r'in_memory\tenYardLines')

# create mile markers for "I35" at every 10 KM
markers = []
with arcpy.da.SearchCursor("I35", 'SHAPE@') as rows:
    for r in rows:
        for i in xrange(0, int(r[0].length), 10000):
            markers.append(r[0].positionAlongLine(i))

arcpy.management.CopyFeatures(markers, r'in_memory\tenkm_markers')

