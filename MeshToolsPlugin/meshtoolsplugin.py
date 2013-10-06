# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MeshToolsPlugin
                                 A QGIS plugin
 Generate and Display unstructured triangular meshes
                              -------------------
        begin                : 2013-03-31
        copyright            : (C) 2013 by Juernjakob Dugge
        email                : juernjakob.dugge@uni-tuebingen.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import qgis.core as qgis
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from meshtoolsplugindialoggenerate import MeshToolsPluginDialogGenerate
# Mesh Tools
import meshtools as mt

import os.path



# Import the utilities from the fTools plugin (a standard QGIS plugin),
# which provide convenience functions for handling QGIS vector layers
import sys, os, imp
import fTools
path = os.path.dirname(fTools.__file__)
ftu = imp.load_source('ftools_utils', os.path.join(path,'tools','ftools_utils.py'))


class MeshToolsPlugin:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/meshtoolsplugin"
        # initialize locale
        localePath = ""
        locale = QSettings().value("locale/userLocale")[0:2]

        if QFileInfo(self.plugin_dir).exists():
            localePath = self.plugin_dir + "/i18n/meshtoolsplugin_" + locale + ".qm"

        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlgGenerate = MeshToolsPluginDialogGenerate(self.iface)
        

    def initGui(self):
        # Create actions
        self.actionGenerate = QAction(
            QIcon(":/plugins/meshtoolsplugin/icon_newmesh.svg"),
            u"Generate Mesh", self.iface.mainWindow())
        self.actionAdd = QAction(
            QIcon(":/plugins/meshtoolsplugin/icon_addmesh.svg"),
            u"Add Mesh", self.iface.mainWindow())
        self.actionSave = QAction(
            QIcon(":/plugins/meshtoolsplugin/icon_savemesh.svg"),
            u"Save Mesh", self.iface.mainWindow())

        
        # Connect actions to functions
        self.actionGenerate.triggered.connect(self.runGenerate)
        self.actionAdd.triggered.connect(self.runAdd)
        self.actionSave.triggered.connect(self.runSave)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.actionGenerate)
        self.iface.addToolBarIcon(self.actionAdd)
        self.iface.addToolBarIcon(self.actionSave)
        
        self.iface.addPluginToMenu(u"&Mesh Tools", self.actionGenerate)
        self.iface.addPluginToMenu(u"&Mesh Tools", self.actionAdd)
        self.iface.addPluginToMenu(u"&Mesh Tools", self.actionSave)
        

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Mesh Tools", self.actionGenerate)
        self.iface.removePluginMenu(u"&Mesh Tools", self.actionAdd)
        self.iface.removePluginMenu(u"&Mesh Tools", self.actionSave)
        
        self.iface.removeToolBarIcon(self.actionGenerate)
        self.iface.removeToolBarIcon(self.actionAdd)
        self.iface.removeToolBarIcon(self.actionSave)



    # run method that performs all the real work
    def runGenerate(self):
        # show the dialog
        self.dlgGenerate.populateLayerComboBoxes()
        self.dlgGenerate.populateAttributeComboBoxes()
        self.dlgGenerate.show()
        # Run the dialog event loop
        result = self.dlgGenerate.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code)
            pass
    
    def runAdd(self):
        fileName = str(QFileDialog.getOpenFileName(self.dlgGenerate, 'Open file', 
                '', "Mesh Tools object (*.pickle);;GridBuilder slice (*.xyc);;All files (*)"))
        if fileName:
            baseName, extension = os.path.splitext(fileName)
            if extension == ".pickle":
                type = "pickle"
            elif extension == ".xyc":
                type = "gb"
            mesh = mt.readMesh(fileName,type)
            self.createMemoryMeshLayer(mesh)
    
    def runSave(self, mesh):
        layer = self.iface.activeLayer()
        if hasattr(layer, 'mesh'):
            fileName = str(QFileDialog.getSaveFileName(self.dlgGenerate, 'Save mesh file', 
                                                       "","GMS 2DM Mesh (*.2dm)"))
            if fileName:
                mt.writeMeshGMS(layer.mesh, fileName)
        else:
            QMessageBox.warning(self.dlgGenerate, 'Mesh Tools',
                                "Selected layer is not a recognised mesh layer. Please select a different layer.")

    def createShapefile(self, fname, geometryType):
        if fname != "":
            try:
                os.remove(fname)
            except OSError:
                 pass
            crs = self.iface.mapCanvas().mapRenderer().destinationCrs()
            fields = { 0 : QgsField("Length", QVariant.Double),
                      1 : QgsField("Type", QVariant.Int) }
            writer = QgsVectorFileWriter(fname, "CP1250", fields, geometryType, crs, "ESRI Shapefile")
            if writer.hasError() != QgsVectorFileWriter.NoError:
                print "Error when creating shapefile: ", writer.hasError()
            del writer
    
def createMemoryMeshLayer(mesh, name="Mesh"):
    vl = QgsVectorLayer("Polygon", name,  "memory")
    pr = vl.dataProvider()
    for index, triangle in enumerate(mesh.elements):
        nodeIDs = triangle[1]
        coordinates = mesh.nodes.coordinates[nodeIDs]
        fet = QgsFeature()
        fet.setGeometry(QgsGeometry.fromPolygon([[
                QgsPoint(*coordinates[0]),
                QgsPoint(*coordinates[1]),
                QgsPoint(*coordinates[2])]]))
        pr.addFeatures( [ fet ] )
    vl.updateExtents()
    QgsMapLayerRegistry.instance().addMapLayer(vl)
    vl.mesh = mesh
    del mesh
        
  
        
def generateMesh(boundaryLayerName='', polygonLayerName='',
                 lineLayerName='', pointLayerName='',
                 triangleEdgeLengthValue=1, triangleEdgeLengthAttribute='',
                 triangleEdgeTypeValue=1, triangleEdgeTypeAttribute='', meshName="Mesh",
                 algorithm="EasyMesh", triangleAngle=0, triangleArea=0,
                 regionLayerName="",regionAttributeName="", netgenGrading=1):
    # Process the polygon layer
    graph = mt.pslGraph()
    graph = addLayerFeaturesToGraph(boundaryLayerName, graph, triangleEdgeLengthAttribute, triangleEdgeLengthValue, triangleEdgeTypeAttribute, triangleEdgeTypeValue)
    if polygonLayerName != "":
        graph = addLayerFeaturesToGraph(polygonLayerName, graph, triangleEdgeLengthAttribute, triangleEdgeLengthValue, triangleEdgeTypeAttribute, triangleEdgeTypeValue)
    if lineLayerName != "":
        graph = addLayerFeaturesToGraph(lineLayerName, graph, triangleEdgeLengthAttribute, triangleEdgeLengthValue, triangleEdgeTypeAttribute, triangleEdgeTypeValue)
    if pointLayerName != "":
        graph = addLayerFeaturesToGraph(pointLayerName, graph, triangleEdgeLengthAttribute, triangleEdgeLengthValue, triangleEdgeTypeAttribute, triangleEdgeTypeValue)
    if algorithm=="EasyMesh":
        mesh = mt.buildMesh(graph, "EasyMesh")
    if algorithm=="Triangle":
        # Define regions
        if regionLayerName != "":
            regionCoords,regionValues = listLayerPointsWithAttribute(regionLayerName,
                                                                 regionAttributeName)
            graph.regions = zip([comp[0] for comp in regionCoords],
                                [comp[1] for comp in regionCoords],
                                [1]*len(regionCoords),
                                regionValues)
        mesh = mt.buildMesh(graph, "Triangle", triangleAngle=triangleAngle,
                            triangleArea=triangleArea)
    if algorithm=="Netgen":
        mesh = mt.buildMesh(graph, "Netgen", netgenGrading = netgenGrading)
    createMemoryMeshLayer(mesh, meshName)
    del mesh

def addLayerFeaturesToGraph(layerName, graph, triangleEdgeLengthAttribute, triangleEdgeLengthValue,
                            triangleEdgeTypeAttribute, triangleEdgeTypeValue):
    layer = ftu.getVectorLayerByName(layerName)
    provider = layer.dataProvider()
    fieldnames = [field.name() for field in provider.fields()]
    for feature in  provider.getFeatures():
        if triangleEdgeLengthAttribute in fieldnames:
            edgeLength = feature[triangleEdgeLengthAttribute]
        else:
            edgeLength = triangleEdgeLengthValue
        
        if triangleEdgeTypeAttribute in fieldnames:
            edgeType = feature[triangleEdgeTypeAttribute]
        else:
            edgeType = triangleEdgeTypeValue
        geometry = feature.geometry()
        graph.addEdges(listAllEdges(geometry), edgeLength, edgeType)
    return graph

def listAllEdges(object):
    type = object.wkbType()
    edges = list()
    if type == qgis.QGis.WKBPoint:
        coord = [tuple([object.asPoint().x(), object.asPoint().y()])]
        edges.extend([(coord[0],coord[0])])
        
    elif type == qgis.QGis.WKBLineString:
        coords = object.geometry().asPolyline()
        coords = [tuple([coord.x(), coord.y()]) for coord in coords]
        edges.extend(zip(coords[:-1],coords[1:]))
        
    elif type == qgis.QGis.WKBPolygon:
        geometry = object.asPolygon()
        orientations = mt.checkPolygonOrientation(geometry)
        
        # Check if outer ring is counterclockwise, reverse if not
        if orientations[0] == -1:
            geometry[0] = geometry[0][::-1]
        # Add the arcs to the edge list
        coords = [tuple([coord.x(), coord.y()]) for coord in geometry[0]]
        edges.extend(zip(coords[:-1],coords[1:]))
        
        # Check if inner rings are clockwise, reverse
        for i, g in enumerate(geometry[1:], 1):
            if orientations[i] == 1:
                geometry[i] = geometry[i][::-1]
            coords = [tuple([coord.x(), coord.y()]) for coord in geometry[i]]
            edges.extend(zip(coords[:-1],coords[1:]))
            
    elif type == qgis.QGis.WKBMultiPolygon:
        for polygon in object.geometry().asPolygon():
            edges.extend(listAllEdges(qgis.QGis.QgsGeometry.fromPolygon(polygon)))
    return edges

def listLayerPointsWithAttribute(layerName, attribute, defaultValue=100):
    layer = ftu.getVectorLayerByName(layerName)
    provider = layer.dataProvider()
    attributeID = provider.fieldNameIndex(attribute)
    provider.select([attributeID])
    feature = QgsFeature()
    coordinates = list()
    attributeValues = list()
    while provider.nextFeature(feature):
        if attributeID != -1:
            attributeValue = feature.attributeMap()[attributeID].toFloat()[0]
        else:
            attributeValue = defaultValue
        coordinates.append(tuple(feature.geometry().asPoint()))
        attributeValues.append(attributeValue)
    return (coordinates, attributeValues)