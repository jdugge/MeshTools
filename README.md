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
