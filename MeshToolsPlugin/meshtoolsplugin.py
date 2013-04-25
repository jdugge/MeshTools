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
import Meshtools.meshtools as mt
import os.path

# Import the utilities from the fTools plugin (a standard QGIS plugin),
# which provide convenience functions for handling QGIS vector layers
import sys, os, imp
import fTools
import ftools_utils
path = os.path.dirname(fTools.__file__)
ftu = imp.load_source('ftools_utils', os.path.join(path,'tools','ftools_utils.py'))
import ftools_utils

import shapely.wkb


class MeshToolsPlugin:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/meshtoolsplugin"
        # initialize locale
        localePath = ""
        locale = QSettings().value("locale/userLocale").toString()[0:2]

        if QFileInfo(self.plugin_dir).exists():
            localePath = self.plugin_dir + "/i18n/meshtoolsplugin_" + locale + ".qm"

        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlgGenerate = MeshToolsPluginDialogGenerate()
        

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
        self.actionSave.triggered.connect(self.runGenerate)

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
        pass
    
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
        
    ###
def getLayerByName(layer_name):
    for name, search_layer in qgis.QgsMapLayerRegistry.instance().mapLayers().iteritems():
        if search_layer.name() == layer_name:
            return search_layer
        return None

def listLayerIDsOfType(layerType):
    return([layerID for layerID in qgis.QgsMapLayerRegistry.instance().mapLayers()
            if qgis.QgsMapLayerRegistry.instance().mapLayer(layerID).type()==layerType])

def listLayerNamesOfType(layerType):
    return([qgis.QgsMapLayerRegistry.instance().mapLayer(layerID).name() for layerID in qgis.QgsMapLayerRegistry.instance().mapLayers()
            if qgis.QgsMapLayerRegistry.instance().mapLayer(layerID).type()==layerType])

def listLayersOfGeometryType(geometry_type):
    if type(geometry_type) != list: geometry_type = [geometry_type]
    selectedlayers = []
    vectorlayerIDs = listLayerIDsOfType(qgis.QgsMapLayer.VectorLayer)
    for layerID in vectorlayerIDs:
        layer = qgis.QgsMapLayerRegistry.instance().mapLayer(layerID)
        provider = layer.dataProvider()
        feat = qgis.QgsFeature()
        if provider.featureAtId(0, feat):
            if feat.geometry().wkbType() in geometry_type:
                selectedlayers.append(layer.name())
    return(selectedlayers)

def populateComboBox(combobox, geometryTypes, allowRaster=True):
    combobox.clear()
    for geometryType in geometryTypes:
        combobox.addItems(listLayersOfGeometryType(geometryTypes))
    if allowRaster:
        combobox.addItems(listLayerNamesOfType(qgis.QgsMapLayer.RasterLayer))

def listLayerAttributes(self, layer):
    return [str(field.name()) for index, field
        in layer.dataProvider().fields().iteritems()]

def setAttributeComboBox(self, signal, attributeComboBox):
    sender = self.dlg.sender()
    layerName = sender.currentText()
    if layerName != '':
        attributeComboBox.setEnabled(True)
        layer = emfhelpers.getLayerByName(self,layerName)
        attributeComboBox.clear()
        attributeComboBox.addItems(listLayerAttributes(self, layer))
    else:
        attributeComboBox.clear()
        attributeComboBox.setEnabled(False)
        
def generateMesh(boundaryLayerName='', polygonLayerName='',
                 lineLayerName='', pointLayerName='',
                 triangleEdgeLengthValue=1, triangleEdgeLengthAttribute='',
                 triangleEdgeTypeValue=1, triangleEdgeTypeAttribute=''):
    # Process the polygon layer
    graph = mt.pslGraph()
    boundaryLayer = ftools_utils.getVectorLayerByName(boundaryLayerName)
    provider = boundaryLayer.dataProvider()
    #lengthAttributeID = provider.fieldNameIndex(self.dlg.ui.cbPolygonsLength.currentText())
    #typeAttributeID = provider.fieldNameIndex(self.dlg.ui.cbPolygonsMarker.currentText())
    #provider.select([lengthAttributeID,typeAttributeID])
    feature = QgsFeature()
    while provider.nextFeature(feature):
        #lengthAttribute = feature.attributeMap()[lengthAttributeID].toFloat()[0]
        #typeAttribute = feature.attributeMap()[typeAttributeID].toInt()[0]
        geometry = shapely.wkb.loads(feature.geometry().asWkb())
        graph.addEdges(listAllEdges(geometry), 10, 1)
        #edgelist = zip(edgelist,itertools.cycle([(lengthAttribute, typeAttribute)]))
        #with open('edgelist.pickle','w') as f:
        #    pickle.dump(edgelist,f)
    mesh = mt.buildMesh(graph)
    createMemoryMeshLayer(mesh, "Mesh")
#    if self.dlg.ui.cbLines.currentText() != '':
#        layer = emfhelpers.getLayerByName(self,self.dlg.ui.cbLines.currentText())
#        provider = layer.dataProvider()
#        lengthAttributeID = provider.fieldNameIndex(self.dlg.ui.cbLinesLength.currentText())
#        typeAttributeID = provider.fieldNameIndex(self.dlg.ui.cbLinesMarker.currentText())
#        provider.select([lengthAttributeID,typeAttributeID])
#        feature = QgsFeature()
#        while provider.nextFeature(feature):
#            lengthAttribute = feature.attributeMap()[lengthAttributeID].toFloat()[0]
#            typeAttribute = feature.attributeMap()[typeAttributeID].toInt()[0]
#            geometry = shapely.wkb.loads(feature.geometry().asWkb())
#            graph.addEdges(emfhelpers.listAllEdges(geometry), lengthAttribute, typeAttribute)
#    
#    if self.dlg.ui.cbPoints.currentText() != '':
#        layer = emfhelpers.getLayerByName(self,self.dlg.ui.cbPoints.currentText())
#        provider = layer.dataProvider()
#        lengthAttributeID = provider.fieldNameIndex(self.dlg.ui.cbPointsLength.currentText())
#        typeAttributeID = provider.fieldNameIndex(self.dlg.ui.cbPointsMarker.currentText())
#        provider.select([lengthAttributeID,typeAttributeID])
#        feature = QgsFeature()
#        while provider.nextFeature(feature):
#            lengthAttribute = feature.attributeMap()[lengthAttributeID].toFloat()[0]
#            typeAttribute = feature.attributeMap()[typeAttributeID].toInt()[0]
#            geometry = shapely.wkb.loads(feature.geometry().asWkb())
#            graph.addEdges(emfhelpers.listAllEdges(geometry)) 

# List all edges of a QGis feature
def listAllEdges(object):
    type = object.geom_type
    edges = list()
    if type == 'Point':
        coord = list(object.coords)
        edges.extend([(coord[0],coord[0])])
    if type == 'LineString' or type == 'LinearRing':
        coords = list(object.coords)
        edges.extend(zip(coords[:-1],coords[1:]))
    if type == 'Polygon':
        object = shapely.geometry.polygon.orient(object)
        edges.extend(listAllEdges(object.exterior))
        for interior in object.interiors:
            edges.extend(listAllEdges(interior))
    elif type == 'MultiPolygon':
        for geom in object.geoms:
            edges.extend(listAllEdges(geom))
    return edges