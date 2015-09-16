import arcpy
import pythonaddins
import sys
import os
import restapi
arcpy.env.overwriteOutput = True

class Clip(object):
    """Implementation for ClipLidarDEM_addin.tool (Tool)"""
    def __init__(self):
        self.enabled = True
        self.shape = 'Rectangle'
        self.cursor = 3

    def onRectangle(self, rectangle_geometry):
        arcpy.env.overwriteOutput = True
        arcpy.env.addOutputsToMap = False
        mxd = arcpy.mapping.MapDocument('current')
        df = mxd.activeDataFrame
        sr = df.spatialReference

        # check input units to make sure they are in meters
        lu = sr.linearUnitName
        if lu.lower() != 'meter':
            msg = 'Spatial Reference linear units are not in meters, ' + \
                  'output cellsize unit: "{}"! Would you like to Continue?'.format(lu)
            choice = pythonaddins.MessageBox(msg, 'Warning', 1)
            if choice.lower() == 'cancel':
                raise RuntimeWarning('User Canceled')

        # make polygon geom obj
        polygon = arcpy.Polygon(arcpy.Array([rectangle_geometry.lowerLeft,
                                             rectangle_geometry.lowerRight,
                                             rectangle_geometry.upperRight,
                                             rectangle_geometry.upperLeft]), sr)
        temp = r'in_memory\temp_poly_xxx'
        arcpy.management.CopyFeatures(polygon, temp)

        # get output raster
        fileName = pythonaddins.SaveDialog('Output DEM', 'dem_clip.tif')
        if not fileName.endswith('.tif'):
            fileName = os.path.splitext(fileName)[0] + '.tif'
        output = arcpy.CreateUniqueName(os.path.basename(fileName), os.path.dirname(fileName))

        # hit MPCA Lidar Image server
        url = 'http://pca-gis02.pca.state.mn.us/arcgis/rest/services/Elevation/DEM_1m/ImageServer'
        im = restapi.ImageService(url)

        try:
            im.clip(temp, output)

            # add output to map
            symb = os.path.join(os.path.dirname(__file__), r'MapData\dem.lyr')
            lyr = arcpy.mapping.Layer(output)
            arcpy.management.ApplySymbologyFromLayer(lyr, symb)
            arcpy.mapping.AddLayer(df, lyr)
            arcpy.RefreshActiveView()

        except:
            pythonaddins.MessageBox(sys.exc_info()[1], 'restapi Error', 0)

        finally:
            del mxd
