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
 This script initializes the plugin, making it known to QGIS.
"""


def name():
    return "Mesh Tools"


def description():
    return "Generate and Display unstructured triangular meshes"


def version():
    return "Version 0.1"


def icon():
    return "icon.png"


def qgisMinimumVersion():
    return "1.8"

def author():
    return "Juernjakob Dugge"

def email():
    return "juernjakob.dugge@uni-tuebingen.de"

def classFactory(iface):
    # load MeshToolsPlugin class from file MeshToolsPlugin
    from meshtoolsplugin import MeshToolsPlugin
    return MeshToolsPlugin(iface)
