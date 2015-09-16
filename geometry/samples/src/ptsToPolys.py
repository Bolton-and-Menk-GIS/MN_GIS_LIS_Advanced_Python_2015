#-------------------------------------------------------------------------------
# Name:        pointsToPolys
#
# Purpose:     MN GIS LIS code sample
#
#-------------------------------------------------------------------------------
import arcpy
import os
arcpy.env.overwriteOutput = True

def getPoly(pt, w, h):
    """calculates polygon corners

    pt -- tuple of coordinates (x, y)
    w -- width of polygon (x length)
    h -- height of polygon (y length)
    """
    x, y = pt
    ll = (x - (w * 0.5), y - (h * 0.5))
    ul = (x - (w * 0.5), y + (h * 0.5))
    ur = (x + (w * 0.5), y + (h * 0.5))
    lr = (x + (w * 0.5), y - (h * 0.5))
    return arcpy.Polygon(arcpy.Array([arcpy.Point(*coords) for coords in [ll,ul,ur,lr,ll]]))

def pointsToPoly(points, output, w=500, h=500, from_field=False, w_field='', h_field=''):
    """Creates polygons from centroids by user defined width and height, does not account for
    angles.

    Required:
        points -- centroid points
        output -- output polygons

    Optional:
        w -- width (constant, in X direction)
        h -- height (constant, in Y direction)
        from_field -- if true, will set width and height from fields. Default is False.
        w_field -- width field.  Ignored if from_field is set to False.
        h_field -- height field.  Ignored if from_field is set to False.
    """

    # copy schema
    desc = arcpy.Describe(points)
    sr = desc.spatialReference
    path, name = os.path.split(output)
    arcpy.management.CreateFeatureclass(path, name, 'POLYGON', points, spatial_reference=sr)

    # create geometry
    fields = [f.name for f in desc.fields if not f.required]
    with arcpy.da.SearchCursor(points, ['SHAPE@XY'] + fields) as rows:
        with arcpy.da.InsertCursor(output, ['SHAPE@'] + fields) as irows:
            if from_field in ('true', True, 1) and all([w_field != None, h_field != None]):
                arcpy.AddMessage('using fields')
                w_ind, h_ind = fields.index(w_field), fields.index(h_field)
                for row in rows:
                    irows.insertRow((getPoly(row[0], row[w_ind+1], row[h_ind+1]),) + row[1:])
            else:
                for row in rows:
                    irows.insertRow((getPoly(row[0], float(w), float(h)),) + row[1:])

    arcpy.AddMessage('Created: "{0}"'.format(output))

if __name__ == '__main__':

    pass
