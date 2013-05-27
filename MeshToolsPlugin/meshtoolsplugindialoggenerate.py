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


# Import the utilities from the fTools plugin (a standard QGIS plugin),
# which provide convenience functions for handling QGIS vector layers
import sys, os, imp
import fTools
path = os.path.dirname(fTools.__file__)
ftu = imp.load_source('ftu', os.path.join(path,'tools','ftools_utils.py'))


class MeshToolsPluginDialogGenerate(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_MeshToolsPlugin()
        self.ui.setupUi(self)
        self.ui.cbAlgorithm.addItems(['EasyMesh','Triangle'])
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
    
    def populateLayerComboBoxes(self):
        self.ui.cbBoundaryPolygons.clear()
        self.ui.cbBoundaryPolygons.addItems(ftu.getLayerNames([qgis.QGis.Polygon]))
        
        for (combobox, geometryType) in [(self.ui.cbPolygons, qgis.QGis.Polygon),
                                         (self.ui.cbLines, qgis.QGis.Line),
                                         (self.ui.cbPoints, qgis.QGis.Point),
                                         (self.ui.cbTriangleBoundaryPolygons, qgis.QGis.Polygon),
                                         (self.ui.cbTriangleBoundaryLines, qgis.QGis.Line),
                                         (self.ui.cbTriangleBoundaryPoints, qgis.QGis.Point),
                                         (self.ui.cbTriangleRefinementPoints, qgis.QGis.Point)]:
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
                fieldNames.update(ftu.getFieldNames(layer))
        self.ui.cbTriangleArea.addItems(list(fieldNames))
    
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
        else:
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

