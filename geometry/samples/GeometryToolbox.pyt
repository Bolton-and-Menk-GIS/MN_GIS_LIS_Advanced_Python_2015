import arcpy
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# custom modules
from ptsAlongLineByField import add_points_along_lines_byField
import ptsToPolys
reload(ptsToPolys)
from ptsToPolys import pointsToPoly
from ExtendLines import ExtendLines


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Geometry Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [AddPointsAlongLineByField, PointsToPolygons, ExtendLinesTool]


class AddPointsAlongLineByField(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Add Points Along Line By Field"
        self.description = "Will construct points along a line by field values"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        fc = arcpy.Parameter(displayName='Line Features',
            name='lines',
            datatype='GPFeatureLayer',
            parameterType='Required',
            direction='Input')

        output = arcpy.Parameter(
            displayName='Output Features',
            name='output_features',
            datatype='DEFeatureClass',
            parameterType='Required',
            direction='Output')

        field = arcpy.Parameter(
            displayName='Split Field',
            name='Split_Field',
            datatype='Field',
            parameterType='Required',
            direction='Input')

        field.parameterDependencies = [fc.name]
        fc.filter.list = ['Polyline']
        return [fc, output, field]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        add_points_along_lines_byField(*[p.valueAsText for p in parameters])

class PointsToPolygons(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Centroids to Polygons"
        self.description = "Generate rectangles from center points"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        fc = arcpy.Parameter(displayName='Point Features',
            name='lines',
            datatype='GPFeatureLayer',
            parameterType='Required',
            direction='Input')

        output = arcpy.Parameter(
            displayName='Output Features',
            name='output_features',
            datatype='DEFeatureClass',
            parameterType='Required',
            direction='Output')

        width = arcpy.Parameter(
            displayName='Width',
            name='Width',
            datatype='GPDouble',
            parameterType='Optional',
            direction='Input')

        height = arcpy.Parameter(
            displayName='Height',
            name='Height',
            datatype='GPDouble',
            parameterType='Optional',
            direction='Input')

        fromField = arcpy.Parameter(
            displayName='From Field',
            name='fromField',
            datatype='GPBoolean',
            parameterType='Optional',
            direction='Input')

        Wfield = arcpy.Parameter(
            displayName='Width Field',
            name='Width_Field',
            datatype='Field',
            parameterType='Optional',
            direction='Input')

        Hfield = arcpy.Parameter(
            displayName='Height Field',
            name='Height_Field',
            datatype='Field',
            parameterType='Optional',
            direction='Input')

        fc.filter.list = ['Point']
        Wfield.parameterDependencies = [fc.name]
        Hfield.parameterDependencies = [fc.name]
        return [fc, output, width, height, fromField, Wfield, Hfield]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        for i in range(5,7):
            parameters[i].enabled = False
        if not parameters[4].altered:
            parameters[4].value = False
        if parameters[4].value == True or parameters[4].altered:
            if parameters[4].value == True:
                setEnable = [False, True]
            else:
                setEnable = [True, False]
            for i in range(2,4):
                parameters[i].enabled = setEnable[0]
            for i in range(5,7):
                parameters[i].enabled = setEnable[1]

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
##        args = []
##        for i, p in enumerate(parameters):
##            if i not in[2,3,4]:
##                args.append(p.valueAsText)
##            else:
##                args.append(p.value)
##        pointsToPoly(*[args])
        arcpy.AddMessage([p.valueAsText for p in parameters])
        pointsToPoly(*[p.valueAsText for p in parameters])

class ExtendLinesTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Extend Lines"
        self.description = "Will extend lines at either the first or last point"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        fc = arcpy.Parameter(displayName='Line Features',
            name='lines',
            datatype='GPFeatureLayer',
            parameterType='Required',
            direction='Input')

        output = arcpy.Parameter(
            displayName='Output Features',
            name='output_features',
            datatype='DEFeatureClass',
            parameterType='Required',
            direction='Output')

        shift = arcpy.Parameter(
            displayName='Shift Factor',
            name='Shift_Factor',
            datatype='Double',
            parameterType='Required',
            direction='Input')

        insert = arcpy.Parameter(
            displayName='Line End',
            name='Line_End',
            datatype='String',
            parameterType='Required',
            direction='Input')

        fc.filter.list = ['Polyline']
        insert.filter.list = ['end', 'start']
        return [fc, output, shift, insert]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if not parameters[3].altered:
            parameters[3].value = 'end'
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        ExtendLines(*[p.valueAsText for p in parameters])
