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
ftu = imp.load_source('ftools_utils', os.path.join(path,'tools','ftools_utils.py'))

class MeshToolsPluginDialogGenerate(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_MeshToolsPlugin()
        self.ui.setupUi(self)
        self.ui.cbAlgorithm.addItems(['EasyMesh','Triangle'])
        self.populateComboBoxes()
        #self.ui.cbPolygons.currentIndexChanged.connect(
        #    lambda: mtp.setAttributeComboBox(self, self.ui.cbLength))
        self.ui.cbPolygons.currentIndexChanged.emit(0)
        self.ui.pbGenerate.clicked.connect(self.generateMesh)
    
    def populateComboBoxes(self):
        self.ui.cbBoundaryPolygons.clear()
        self.ui.cbBoundaryPolygons.addItems(ftu.getLayerNames([qgis.QGis.Polygon]))
        
        for (combobox, geometryType) in [(self.ui.cbPolygons, qgis.QGis.Polygon),
                                         (self.ui.cbLines, qgis.QGis.Line),
                                         (self.ui.cbPoints, qgis.QGis.Point)]:
            combobox.clear()
            combobox.addItem('')
            combobox.addItems(ftu.getLayerNames([geometryType]))
        #mtp.populateComboBox(self.ui.cbPolygons, [qgis.QGis.WKBPolygon], allowRaster=False)
        self.ui.cbLength.addItems(["Length","Type"])
    
    def generateMesh(self):
        boundaryLayerName = self.ui.cbBoundaryPolygons.currentText()
        if boundaryLayerName == "":
            QtGui.QMessageBox.warning(self, 'EasyMesh Frontend',
                                "Please select a polygon layer for the boundary of the meshing area")
            return
        mtp.generateMesh(boundaryLayerName)
        
   
