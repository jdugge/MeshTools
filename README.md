MeshTools
=========

QGIS plugin for generating unstructured triangular meshes.

The plugin acts as an interface between QGIS and different mesh generation programs. Vector layers are translated into geometry descriptions that are then fed to the mesh generation program, and the resulting mesh is read into QGIS where it is displayed as a polygon layer. The mesh can then be exported to be used in finite element analysis.

###Features

* Generate unstructured triangular meshes from vector layers in QGIS using the following algorithms:
 * Bojan Niceno's [EasyMesh](http://www-dinma.univ.trieste.it/nirftc/research/easymesh/easymesh.html)
 * Jonathan R. Shewchuk's [Triangle](http://www.cs.cmu.edu/~quake/triangle.html)
* Read existing meshes generated using Rob McLaren's [GridBuilder](http://www.science.uwaterloo.ca/~mclaren/) (the native format for the [HydroGeoSphere groundwater modelling software](http://www.aquanty.com/hgs-tehcnology/))
* Write meshes in the [GMS 2DM](http://www.aquaveo.com/gms) format, which can be used directly in HydroGeoSphere

###Installation
####Linux
* Install the mesh generators
  * EasyMesh: [Download the source](http://www-dinma.univ.trieste.it/nirftc/research/easymesh/download.html), [compile it](http://www-dinma.univ.trieste.it/nirftc/research/easymesh/compilation.html), and make sure that the executable is available as `Easy` in the path (you should be able to type `Easy` at the command prompt and see EasyMesh's welcome screen.
  * Triangle: Install Andreas Kloeckner's [MeshPy python library](https://pypi.python.org/pypi/MeshPy), which acts as a Python interface to the Triangle mesh generator.
* Download the MeshTools project and move the `MeshToolsPlugin` folder to the QGIS plugin directory (typically `~/.qgis/python/plugins/`)
* Activate the plugin in QGIS by going to Plugins / Manage Plugins, finding the entry for "Mesh Tools", checking the box, and clicking OK.


####Windows
* Make sure you have installed QGIS using the [OSGEO4W repository](http://hub.qgis.org/projects/quantum-gis/wiki/Download#12-OSGeo4W-Installer) (this includes many of the depencies usually missing on a Windows system).
* Install the [Windows package](http://www.lfd.uci.edu/~gohlke/pythonlibs/#meshpy) of Andreas Kloeckner's [MeshPy python library](https://pypi.python.org/pypi/MeshPy), which acts as a Python interface to the Triangle mesh generator. Currently, only the Triangle mesh generator works on Windows.
* Download the MeshTools project and move the `MeshToolsPlugin` folder to the QGIS plugin directory (something like `c:\Program Files\Quantum GIS Lisboa\apps\qgis\python\plugins`)
* Activate the plugin in QGIS by going to Plugins / Manage Plugins, finding the entry for "Mesh Tools", checking the box, and clicking OK.

###Usage
#### Generating a new mesh
Open the main dialog by clicking the "Generate Mesh" button ![Generate Mesh button](/MeshToolsPlugin/icon_newmesh.png)

First, you need to decide which algorithm you want to use by selecting the entry from the first drop-down box (if you're using Windows, "Triangle" will be pre-selected and the drop-down box will be greyed out).

##### Triangle
The Triangle algorithm expects a geometry consisting of a bounding polygon and optionally lines and points within that polygon.

If you already have layers loaded in your QGIS project, you can select the ones you want to use for the meshing using the drop-down boxes.

If you want to create new layers, you can click the "New" button to the right of the drop-down boxes. You will be asked for a file name to save the newly created layer. After that, you will see the main QGIS window in editing mode, so you can immediately start adding new features by left-clicking on the canvas. To finish a polygon or line feature, right-click on the final point. You can then enter a value for the desired triangle element area.

To finish creating the new layer, click the "Toggle Editing" button on the main toolbar. You will be taken back to the Mesh Tools dialog.

You can then adjust the settings for the mesh quality: The maximum corner angle (highest value is 34) and the maximum triangle area. The maximum triangle area can either be set to a constant value for the entire mesh, or you can use a point layer to define different maximum triangle areas for different zones of the geometry. Note that these zones need to be separated using lines or polygons. See [the Triangle homepage](http://www.cs.cmu.edu/~quake/triangle.html) for more details on this.

Optionally, you can set a name for the newly created mesh. This will be used to identify the mesh layer added to the QGIS project.

You can then start the mesh generation by clicking "Generate mesh". Depending on the ratio of geometry extent and triangle size, this can take a while (no progress bar yet, sorry). Once the mesh has been generated, it is loaded into the QGIS project.

#### Exporting a mesh
To export a mesh, select the mesh layer in the QGIS layer manager, and then click the "Save Mesh" button ![Save Mesh button](/MeshToolsPlugin/icon_savemesh.png). You will be prompted for a location and file name to save the mesh. You can choose the output format using the drop-down box in the lower right-hand corner. To use the mesh in HydroGeoSphere, choose `2DM`.
