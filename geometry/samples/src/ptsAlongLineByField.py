# from my answer here:
#   http://gis.stackexchange.com/questions/139386/script-to-convert-line-segments-to-equally-spaced-points-based-the-duration-betw/139410#139410
import arcpy
import os
import numpy
arcpy.env.overwriteOutput = True

# could probably come up with a better name for this...
def add_points_along_lines_byField(feats, output, split_field):
    '''Splits lines by a distance or percentage

    Required:
    feats -- input features
    output -- output line feature class
    split_field -- field for number of splits, line length is divided
        by the value of this field
    '''
    def _range(stop, step):
        return [i for i in numpy.arange(0, stop+1, step)
                if i > 0 and i <= stop]

    # create fc's
    path, name = os.path.split(output)
    sm = 'SAME_AS_TEMPLATE'
    output = arcpy.CreateFeatureclass_management(path, name, 'POINT',
                                        feats, sm, sm, feats).getOutput(0)

    # add 'PT_DIST' field
    add_fields = ['LINE_POS', 'SEG_LENGTH']
    for field in add_fields:
        arcpy.AddField_management(output, field, 'DOUBLE')

    # loop thru geom
    fields = [f.name for f in arcpy.ListFields(feats) if not f.required]
    fields.insert(0, 'SHAPE@')
    sec_id = fields.index(split_field)

    # Cursors
    irows = arcpy.da.InsertCursor(output, fields + add_fields)
    with arcpy.da.SearchCursor(feats, fields) as rows:
        for row in rows:
            length = row[0].length
            seg_leng = length / row[sec_id]
            irows.insertRow((row[0].firstPoint,) + row[1:] + (0,0)) #do we need to add the start point?

            # step through each distance
            for i in _range(length, seg_leng):
                pt = row[0].positionAlongLine(i)
                irows.insertRow((pt,) + row[1:] + (i, seg_leng))
    del irows
    return output
