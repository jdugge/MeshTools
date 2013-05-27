'''
Created on Mar 23, 2013

@author: Juernjakob Dugge
'''

import itertools
import subprocess
import os.path
import csv
import struct
import numpy as np
import tempfile
import pickle
import qgis.core as qgis
import PyQt4.QtCore as pyqt


from qgis.core import *
log = lambda m: QgsMessageLog.logMessage(m,'My Plugin') 


class pslGraph():
    '''Planar Straight Line Graph that is used to define the geometry
    for generating meshes'''
    def __init__(self):
        self.curIndex=0
        self.lengthAttributes = []
        self.typeAttributes = []
        self.edges = []
        self.regions = [] # Used by Triangle algorithm to specify maximum triangle areas
    def __iter__(self):
        return self
    def next(self):
        self.curIndex += 1
        if self.curIndex < len(self.edges):
            return (self.lengthAttributes[self.curIndex], self.edges[self.curIndex])
        else:
            self.curIndex=0
            raise StopIteration
    def addEdges(self, edges, lengthAttribute, typeAttribute):
        '''Takes a list of coordinate pairs, a length attribute,
        and a type attribute. The attributes are assigned to all
        edges in the list.'''
        self.edges.extend(edges)
        self.lengthAttributes.extend([lengthAttribute]*len(edges))
        self.typeAttributes.extend([typeAttribute]*len(edges))
    def nodesList(self):
        '''List of all unique node coordinates in the graph,
        in no particular order'''
        return list(set(itertools.chain.from_iterable(self.edges)))
    def asNodeIndices(self):
        '''Graph expressed in terms of node indices,
        indices corresponding to the output of pslGraph.nodesList()'''
        return [tuple([self.nodesList().index(coordinate) for coordinate in edge]) for edge in self.edges]
    def lengthAttributesList(self):
        '''List of length attributes,
        corresponding to the output of pslGraph.nodesList()'''
        lengths = [0]*len(self.nodesList())
        for index,edge in enumerate(self.asNodeIndices()):
            for node in edge:
                lengths[node] = self.lengthAttributes[index]
                pass
        return lengths
    def typeAttributesList(self):
        '''List of type attributes,
        corresponding to the output of pslGraph.nodesList()'''
        types = [0]*len(self.nodesList())
        for index,edge in enumerate(self.asNodeIndices()):
            for node in edge:
                types[node] = self.typeAttributes[index]
                pass
        return types

class triangleMesh():
    '''Unstructured triangular mesh.
    Consists of mesh nodes and triangular mesh elements'''
    def __init__(self):
        self.nodes = meshNodes()
        self.elements = meshElements()
    def __call__(self):
        print "Triangle mesh\nNumber of elements: " + (str(len(self.elements.numbers)) + "\nNumber of nodes: " + str(len(self.nodes.numbers)))
    def asCoordinateList(self):
        '''List of node coordinates'''
        return self.nodes.coordinates[self.elements.nodes]
    def angles(self):
        elements = self.asCoordinateList()
        L = np.roll(elements,-1,1) - elements
        segmentAngles = np.rad2deg(np.arctan2(L[:,:,1],L[:,:,0]))
        angles = np.mod(180 - (np.roll(segmentAngles,-1,1) - segmentAngles),360)
        return angles

class meshNodes():
    def __init__(self):
        self.curIndex=0
        self.numbers = []
        self.coordinates = []
        self.markers = []
    def __len__(self):
        return len(self.markers)
    def __iter__(self):
        return self
    def next(self):
        self.curIndex += 1
        if self.curIndex <= len(self.markers):
            return self.coordinates[self.curIndex-1]
        else:
            self.curIndex=0
            raise StopIteration

class meshElements():
    def __init__(self):
        self.curIndex=0
        self.numbers = []
        self.nodes = []
        self.markers = []
    def __len__(self):
        return len(self.markers)
    def __getitem__(self, index):
        return [self.numbers[index], self.nodes[index], self.markers[index]]
    def __iter__(self):
        return self
    def next(self):
        self.curIndex += 1
        if self.curIndex <= len(self.markers):
            return self[self.curIndex-1]
        else:
            self.curIndex=0
            raise StopIteration

def buildMesh(geometry, algorithm="EasyMesh", triangleAngle=0, triangleArea=0):
    if algorithm=="EasyMesh":
        tempFileFD, tempFileName = tempfile.mkstemp(suffix=".d", text=True)
        tempFileBaseName, tempFileExtension = os.path.splitext(tempFileName)
        writeEasyMeshInput(geometry, tempFileName)
        runEasyMesh(tempFileName)
        mesh = readEasyMeshOutput(tempFileBaseName)
        return mesh
    elif algorithm=="Triangle":
        import meshpy.triangle as tri
        info = tri.MeshInfo()
        info.set_points(geometry.nodesList())
        info.set_facets(geometry.asNodeIndices())
        info.regions.resize(len(geometry.regions))
        for i,region in enumerate(geometry.regions):
            info.regions[i] = list(region)
        log(str(info.regions[0]))
        triMesh = tri.build(info,min_angle=triangleAngle, attributes=True,
                            volume_constraints=True)
        mesh = triangleMesh()
        mesh.nodes.coordinates = np.array(triMesh.points)
        mesh.nodes.numbers = range(len(mesh.nodes.coordinates))
        mesh.elements.nodes = np.array(triMesh.elements)
        mesh.elements.numbers = range(len(mesh.elements.nodes))
        mesh.elements.markers = [1]*len(mesh.elements.nodes)
        return mesh

    
def writeEasyMeshInput(geometry, filename):
    '''Write graph to a file in a format that can be used
    by the EasyMesh mesh generator'''
    if filename[-2:] != '.d':
        print "filename should end in '.d'"
        return
    with open(filename,'w') as f:
        f.write(str(len(geometry.nodesList())))
        f.write('\n')
        for index,(node,length,typeAttribute) in enumerate(zip(geometry.nodesList(),
                                                  geometry.lengthAttributesList(),
                                                  geometry.typeAttributesList())):
            f.write(str(index) + '\t')
            f.write('\t'.join([str(component) for component in node]))
            f.write('\t' + str(length) +'\t'+
                     str(typeAttribute) + '\n')
        f.write('\n' + str(len(geometry.edges)) + '\n')
        for index,edge in enumerate(geometry.asNodeIndices()):
            f.write(str(index) + '\t' + '\t'.join([str(component) for component in edge]) + '\t1\n')

def runEasyMesh(filename):
    rootfilename = os.path.join(os.path.dirname(filename),os.path.splitext(os.path.basename(filename))[0])
    subprocess.call(["EasyMesh", filename,"+dxf"])
    mesh = readEasyMeshOutput(rootfilename)
    return mesh
    
def readEasyMeshOutput(rootfilename):
    '''Read the output of an EasyMesh run.
    Expects the root file name (without '.d')'''
    mesh = triangleMesh()
    # Read node file
    # <node number:> <x> <y> <marker>
    with open(''.join((rootfilename,'.n'))) as f:
        csvreader = csv.reader(f, delimiter=' ',skipinitialspace=True)
        numberOfLines = int(csvreader.next()[0])
        mesh.nodes.numbers = np.zeros((numberOfLines), dtype=np.int)
        mesh.nodes.coordinates = np.zeros((numberOfLines,2))
        mesh.nodes.markers = np.zeros((numberOfLines), dtype=np.int)
        for i in range(numberOfLines):
            line = csvreader.next()
            mesh.nodes.numbers[i] = int(line[0][0:-1])
            mesh.nodes.coordinates[i] = [float(line[1]), float(line[2])]
            mesh.nodes.markers[i] = int(line[3])
    
    # Read elements file
    # <element number:> <i> <j> <k> <ei> <ej> <ek> <si> <sj> <sk> <xV> <yV> <marker>
    with open(''.join((rootfilename,'.e'))) as f:
        csvreader = csv.reader(f, delimiter=' ',skipinitialspace=True)
        numberOfLines = int(csvreader.next()[0])
        
        mesh.elements.numbers = np.zeros((numberOfLines), dtype=np.int)
        mesh.elements.nodes = np.zeros((numberOfLines,3), dtype=np.int)
        mesh.elements.markers = np.zeros((numberOfLines), dtype=np.int)
        
        for i in range(numberOfLines):
            line = csvreader.next()
            mesh.elements.numbers[i] = int(line[0][0:-1])
            mesh.elements.nodes[i] = [int(number) for number in line[1:4]]
            mesh.elements.markers[i] = int(line[12])
    return mesh



def readGridBuilderSlice(filename):
    mesh = triangleMesh()
    filename = os.path.splitext(filename)[0]
    # Node coordinates
    # so what?
    gbXYCdtype = np.dtype('2f8')
    f = open(''.join([filename,'.xyc']))
    nNodes = struct.unpack('3i',f.read(12))[1]
    nDataBytes = struct.unpack('i',f.read(4))[0]
    data = np.fromstring(f.read(nDataBytes),gbXYCdtype)
    f.close()
    mesh.nodes.numbers = np.arange(nNodes)
    mesh.nodes.coordinates = data
    mesh.nodes.markers = np.ones([nNodes,1], dtype=int)
    
    # Element incidences
    gbIN3dtype = np.dtype('3i')
    f = open(''.join([filename,'.in3']))
    nElements = struct.unpack('3i',f.read(12))[1]
    nDataBytes = struct.unpack('i',f.read(4))[0]
    data = np.fromstring(f.read(nDataBytes),gbIN3dtype)
    mesh.elements.numbers = np.arange(nElements)
    mesh.elements.nodes = data-1
    mesh.elements.markers = np.ones([nElements,1],dtype=int)
    f.close()
    return mesh


# Export functions

def writeMeshShapefile(mesh, fileName, crs=None):
        try:
            os.remove(fileName)
        except OSError:
            pass
        fields = { 0 : qgis.QgsField("ID", pyqt.QVariant.Int),
                  1 : qgis.QgsField("Marker", pyqt.QVariant.Int),
                  2 : qgis.QgsField("Node1", pyqt.QVariant.Int),
                  3 : qgis.QgsField("Node2", pyqt.QVariant.Int),
                  4 : qgis.QgsField("Node3", pyqt.QVariant.Int)  }
        writer = qgis.QgsVectorFileWriter(fileName, "utf-8", fields, qgis.QGis.WKBPolygon, crs, "ESRI Shapefile")
        if writer.hasError() != qgis.QgsVectorFileWriter.NoError:
            print "Error when creating shapefile: ", writer.hasError()
        for index, triangle in enumerate(mesh.elements):
            nodeIDs = triangle[1]
            coordinates = mesh.nodes.coordinates[nodeIDs]
            fet = qgis.QgsFeature()
            fet.setGeometry(qgis.QgsGeometry.fromPolygon([[
                    qgis.QgsPoint(*coordinates[0]),
                    qgis.QgsPoint(*coordinates[1]),
                    qgis.QgsPoint(*coordinates[2])]]))
            fet.addAttribute(0, pyqt.QVariant(index))
            fet.addAttribute(1, pyqt.QVariant(1))
            fet.addAttribute(2, pyqt.QVariant(1))
            writer.addFeature(fet)

# delete the writer to flush features to disk (optional)
        del writer

def writeMeshGMS(mesh, filename):
    VerticesString = [' '.join( ['ND', str(index+1), ' '.join(map(str, node))] ) for index,node in enumerate(mesh.nodes.coordinates)]
    TrianglesString = [' '.join( ['E3T', str(index+1), ' '.join(map(str, triangle)), '0'] ) for index,triangle in enumerate(mesh.elements.nodes+1)]
    
    with open(filename,'w') as f:
        f.write('MESH2D\n')
        for vertex in VerticesString:
            f.write(vertex)
            f.write('\n')
        for triangle in TrianglesString:
            f.write(triangle)
            f.write('\n')

def writeMeshPickle(mesh, fileName):
    with open(fileName, 'w') as f:
        pickle.dump(mesh,f)

def readMeshPickle(fileName):
    with open(fileName,'r') as f:
        mesh = pickle.load(f)
    return mesh

def readMesh(fileName, type="pickle"):
    type = type.lower()
    
    if type == "pickle":
        mesh = readMeshPickle(fileName)
    elif type == "gms":
        #mesh = readMeshGMS(fileName)
        pass
    elif type == "gb" or type == "gridbuilder":
        mesh = readGridBuilderSlice(fileName)
    
    return mesh