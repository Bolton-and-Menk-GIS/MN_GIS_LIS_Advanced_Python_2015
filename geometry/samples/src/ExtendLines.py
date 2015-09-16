import arcpy
import os
arcpy.env.overwriteOutput = True

def ExtendLines(lines, out, shift, insert='end'):
    '''This tool will extend an airport runway by a user specified distance.

    Required: 
        lines -- input runway to extend
        out -- output line feature class with extended runway
        shift -- linear footage to add to either first or last point

    Optional:
        insert -- option to choose to insert runway extension at either the first or last point
    '''

    # spatial reference
    desc = arcpy.Describe(lines)
    SR = desc.spatialReference

    # Copy features
    arcpy.management.CopyFeatures(lines, out)

    # Search and insert cursors
    with arcpy.da.UpdateCursor(out, ['SHAPE@']) as rows:
        for row in rows:
            # grab geom
            geom = row[0]
            gf = geom.firstPoint
            gl = geom.lastPoint
            length = geom.length
            
            # get first and last x,y
            fx,fy = gf.X,gf.Y
            lx,ly = gl.X,gl.Y
            last = gl.Z
            first = gf.Z
            
            # determine direction
            if insert.lower() == 'end':
                x_diff = lx - fx
                y_diff = ly - fy
                x_fact = x_diff / length 
                y_fact = y_diff / length
                add_x =  lx + (x_fact * float(shift))
                add_y =  ly + (y_fact * float(shift))
            else:
                # first point
                x_diff = fx - lx
                y_diff = fy - ly
                x_fact = x_diff / length 
                y_fact = y_diff / length
                add_x =  fx + (x_fact * float(shift))
                add_y =  fy + (y_fact * float(shift))

            # new line segment for geometry
            # grab z value of last point
            array = arcpy.Array()
            for i in range(geom.partCount):
                prt = geom.getPart(i)
                for point in prt:
                    array.add(point)
            if insert.lower() == 'end':
                array.append(arcpy.Point(add_x, add_y, last))
            else:
                array.insert(0, arcpy.Point(add_x, add_y, first))
            rows.updateRow([arcpy.Polyline(array, SR, True)])
    arcpy.AddMessage('Extended lines')
    return

if __name__ == '__main__':

    # Get Args
    argv = tuple(arcpy.GetParameterAsText(i) for i in range(arcpy.GetArgumentCount()))

    # Run tool
    ExtendLines(*argv)
