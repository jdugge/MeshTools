# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MeshToolsPluginDialogGenerate
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

from PyQt4 import QtCore, QtGui
from ui_meshtoolsplugin import Ui_MeshToolsPlugin
import qgis.core as qgis
import meshtoolsplugin as mtp

import types


# Import the utilities from the fTools plugin (a standard QGIS plugin),
# which provide convenience functions for handling QGIS vector layers
import sys, os, imp, platform
import fTools
path = os.path.dirname(fTools.__file__)
ftu = imp.load_source('ftu', os.path.join(path,'tools','ftools_utils.py'))


class MeshToolsPluginDialogGenerate(QtGui.QDialog):
    def __init__(self, iface):
        QtGui.QDialog.__init__(self)
        self.iface = iface
        # Set up the user interface from Designer.
        self.ui = Ui_MeshToolsPlugin()
        self.ui.setupUi(self)
        self.ui.cbAlgorithm.addItems(['EasyMesh','Triangle', 'Netgen'])
        self.ui.cbAlgorithm.setCurrentIndex(1)
        if (platform.system()=='Windows'):
            self.ui.cbAlgorithm.setEnabled(False)
        #self.ui.cbPolygons.currentIndexChanged.connect(
        #    lambda: mtp.setAttributeComboBox(self, self.ui.cbLength))
        
        # Trigger repopulation of attribute comboboxes with changes layer comboboxes
        self.ui.cbBoundaryPolygons.currentIndexChanged.connect(self.populateAttributeComboBoxes)
        self.ui.cbPolygons.currentIndexChanged.connect(self.populateAttributeComboBoxes)
        self.ui.cbLines.currentIndexChanged.connect(self.populateAttributeComboBoxes)
        self.ui.cbPoints.currentIndexChanged.connect(self.populateAttributeComboBoxes)
        
        self.ui.cbTriangleRefinementPoints.currentIndexChanged.connect(self.populateTriangleComboBox)
        
        self.ui.cbPolygons.currentIndexChanged.emit(0)
        self.ui.pbGenerate.clicked.connect(self.generateMesh)
        self.ui.pbTriangleNewPoints.clicked.connect(
            lambda: self.createNewLayer(qgis.QGis.WKBPoint, self.ui.cbTriangleBoundaryPoints,
                                        { 0 : qgis.QgsField("Element Area", QtCore.QVariant.Double)}))
        self.ui.pbTriangleNewPolygons.clicked.connect(
            lambda: self.createNewLayer(qgis.QGis.WKBPolygon, self.ui.cbTriangleBoundaryPolygons,
                                        { 0 : qgis.QgsField("Element Area", QtCore.QVariant.Double)}))
        self.ui.pbTriangleNewLines.clicked.connect(
            lambda: self.createNewLayer(qgis.QGis.WKBLineString, self.ui.cbTriangleBoundaryLines,
                                        { 0 : qgis.QgsField("Element Area", QtCore.QVariant.Double)}))
        self.ui.pbTriangleRefinementNewPoints.clicked.connect(
            lambda: self.createNewLayer(qgis.QGis.WKBPoint, self.ui.cbTriangleRefinementPoints,
                                        { 0 : qgis.QgsField("Element Area", QtCore.QVariant.Double)}))
        self.ui.pbNewPolygons.clicked.connect(
            lambda: self.createNewLayer(qgis.QGis.WKBPolygon, self.ui.cbPolygons,
                                        { 0 : qgis.QgsField("Edge Length", QtCore.QVariant.Double),
                                         1 : qgis.QgsField("Edge Type", QtCore.QVariant.Double)}))
        self.ui.pbNewLines.clicked.connect(
            lambda: self.createNewLayer(qgis.QGis.WKBLineString, self.ui.cbLines,
                                        { 0 : qgis.QgsField("Edge Length", QtCore.QVariant.Double),
                                         1 : qgis.QgsField("Edge Type", QtCore.QVariant.Double)}))
        self.ui.pbNewPoints.clicked.connect(
            lambda: self.createNewLayer(qgis.QGis.WKBPoint, self.ui.cbPoints,
                                        { 0 : qgis.QgsField("Edge Length", QtCore.QVariant.Double),
                                         1 : qgis.QgsField("Edge Type", QtCore.QVariant.Double)}))
        self.ui.pbNewBoundaryPolygons.clicked.connect(
            lambda: self.createNewLayer(qgis.QGis.WKBPolygon, self.ui.cbBoundaryPolygons,
                                        { 0 : qgis.QgsField("Edge Length", QtCore.QVariant.Double),
                                         1 : qgis.QgsField("Edge Type", QtCore.QVariant.Double)}))
        
         
    def populateLayerComboBoxes(self):
        # Boundary polygons are always needed, so don't include an empty entry in those comboBoxes
        self.ui.cbBoundaryPolygons.clear()
        self.ui.cbBoundaryPolygons.addItems(ftu.getLayerNames([qgis.QGis.Polygon]))
        self.ui.cbTriangleBoundaryPolygons.clear()
        self.ui.cbTriangleBoundaryPolygons.addItems(ftu.getLayerNames([qgis.QGis.Polygon]))
        
        
        for (combobox, geometryType) in [(self.ui.cbPolygons, qgis.QGis.Polygon),
                                         (self.ui.cbLines, qgis.QGis.Line),
                                         (self.ui.cbPoints, qgis.QGis.Point),
                                         (self.ui.cbTriangleBoundaryLines, qgis.QGis.Line),
                                         (self.ui.cbTriangleBoundaryPoints, qgis.QGis.Point),
                                         (self.ui.cbTriangleRefinementPoints, qgis.QGis.Point),
                                         (self.ui.cbNetgenBoundaryPolygons, qgis.QGis.Polygon)]:
            combobox.clear()
            combobox.addItem('')
            combobox.addItems(ftu.getLayerNames([geometryType]))
            
        #mtp.populateComboBox(self.ui.cbPolygons, [qgis.QGis.WKBPolygon], allowRaster=False)
        #self.ui.cbLength.addItems(["Length","Type"])
    
    def populateAttributeComboBoxes(self):
        self.ui.cbLength.clear()
        self.ui.cbType.clear()
        fieldNames = set()
        for combobox in [self.ui.cbBoundaryPolygons, self.ui.cbPolygons,
                         self.ui.cbLines, self.ui.cbPoints]:
            if (combobox.currentText() != ""):
                layer = ftu.getVectorLayerByName(combobox.currentText())
                if (type(layer) != types.NoneType):
                    fieldNames.update(ftu.getFieldNames(layer))
        #QtCore.QStringList(fieldNames)
        self.ui.cbLength.addItems(list(fieldNames))
        self.ui.cbType.addItems(list(fieldNames))
    
    def populateTriangleComboBox(self):
        self.ui.cbTriangleArea.clear()
        fieldNames = set()
        for combobox in [self.ui.cbTriangleRefinementPoints]:
            if (combobox.currentText() != ""):
                layer = ftu.getVectorLayerByName(combobox.currentText())
                if (type(layer) != types.NoneType):
                    fieldNames.update(ftu.getFieldNames(layer))
        self.ui.cbTriangleArea.addItems(list(fieldNames))

    def createNewLayer(self, geometryType, comboBox, fields):
        fname = QtGui.QFileDialog.getSaveFileName(self, 'Open file', 
                                        "", "Shapefile (*.shp);;All files (*)")
        fname = os.path.splitext(str(fname))[0]+'.shp'
        layername = os.path.splitext(os.path.basename(str(fname)))[0]
        if (layername=='.shp'):
            return
        self.createShapefile(fname, geometryType, fields)
        vlayer = qgis.QgsVectorLayer(fname, layername, "ogr")
        qgis.QgsMapLayerRegistry.instance().addMapLayer(vlayer)
        comboBox.addItem(layername)
        comboBox.setCurrentIndex(comboBox.count()-1)
        self.populateTriangleComboBox()
        self.iface.actionToggleEditing().trigger()
        self.iface.actionAddFeature().trigger()
        self.iface.actionToggleEditing().triggered.connect(self.showDialogAndDisconnect)
        self.hide()

    def showDialogAndDisconnect(self):
        self.show()
        self.iface.actionToggleEditing().triggered.disconnect(self.showDialogAndDisconnect)
        
    def createShapefile(self, fname, geometryType, fields):
        if fname != "":
            try:
                os.remove(fname)
            except OSError:
                 pass
            crs = self.iface.mapCanvas().mapRenderer().destinationCrs()
            writer = qgis.QgsVectorFileWriter(fname, "CP1250", fields, geometryType, crs, "ESRI Shapefile")
            if writer.hasError() != qgis.QgsVectorFileWriter.NoError:
                print "Error when creating shapefile: ", writer.hasError()
            del writer
    
    def generateMesh(self):
        if self.ui.cbAlgorithm.currentText() == "EasyMesh":
            boundaryLayerName = self.ui.cbBoundaryPolygons.currentText()
            if boundaryLayerName == "":
                QtGui.QMessageBox.warning(self, 'Mesh Tools',
                                    "Please select a polygon layer for the boundary of the meshing area")
                return
            
            # Default edge length value
            edgeLengthValue = float(self.ui.leLength.text())
            
            # Default edge type value
            edgeTypeValue = self.ui.sbType.value()
            
            if self.ui.chkbLengthFromLayer.isChecked():
                edgeLengthAttribute = self.ui.cbLength.currentText()
            else:
                edgeLengthAttribute = ""
            
            if self.ui.chkbTypeFromLayer.isChecked():
                edgeTypeAttribute = self.ui.cbType.currentText()
            else:
                edgeTypeAttribute = ""
            polygonLayerName = self.ui.cbPolygons.currentText()
            lineLayerName = self.ui.cbLines.currentText()
            pointLayerName = self.ui.cbPoints.currentText()
            
            mtp.generateMesh(boundaryLayerName, polygonLayerName, lineLayerName, pointLayerName,
                              triangleEdgeLengthValue=edgeLengthValue,
                             triangleEdgeLengthAttribute=edgeLengthAttribute,
                             triangleEdgeTypeValue=edgeTypeValue,
                             triangleEdgeTypeAttribute=edgeTypeAttribute,
                             meshName=self.ui.leMeshName.text())
        elif self.ui.cbAlgorithm.currentText() == "Triangle":
            boundaryLayerName = self.ui.cbTriangleBoundaryPolygons.currentText()
            if boundaryLayerName == "":
                QtGui.QMessageBox.warning(self, 'Mesh Tools',
                                    "Please select a polygon layer for the boundary of the meshing area")
                return
            lineLayerName = self.ui.cbTriangleBoundaryLines.currentText()
            pointLayerName = self.ui.cbTriangleBoundaryPoints.currentText()
            if self.ui.cbTriangleAngle.isChecked():
                triangleAngle = self.ui.sbTriangleAngle.value()
            else:
                triangleAngle = 30
            if self.ui.leTriangleArea.text() != "":
                triangleArea=float(self.ui.leTriangleArea.text())
            else:
                triangleArea=""
            mtp.generateMesh(boundaryLayerName,lineLayerName=lineLayerName,
                             pointLayerName=pointLayerName,
                             meshName=self.ui.leMeshName.text(),
                             algorithm="Triangle", triangleAngle=triangleAngle,
                             triangleArea=triangleArea,
                             regionLayerName=self.ui.cbTriangleRefinementPoints.currentText(),
                             regionAttributeName=self.ui.cbTriangleArea.currentText())
        elif self.ui.cbAlgorithm.currentText() == "Netgen":
            boundaryLayerName = self.ui.cbNetgenBoundaryPolygons.currentText()
            if boundaryLayerName == "":
                QtGui.QMessageBox.warning(self, 'Mesh Tools',
                                    "Please select a polygon layer for the boundary of the meshing area")
                return
            mtp.generateMesh(boundaryLayerName,
                             meshName=self.ui.leMeshName.text(),
                             algorithm="Netgen")
