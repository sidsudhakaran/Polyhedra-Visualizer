# Polyhedron Visualizer

This repo allows to read and display any 3D object from a comma-separated text file specified by the user. In addition, it allows for click and drag functionality to move and rotate the object. 

The format of the file is:
1. The first line contains two integers. The first integer is the number of vertices that define the 3D object, and the second number is the number of faces that define the 3D object.
2. The following lines define one vertex of the 3D object and will consist of an integer (vertex ID) followed by three real numbers (x, y, z coordinates). 
3. The next section consists of faces. Each line in this section will consist of integers (vertex IDs) that define the face of the object. 

Two sample files -- `cube.txt` and `polyhedron.txt` are provided as sample text files. 

## Getting Started

The code is implemented using Python3 and uses the external ```numpy``` library for matrix operations. In addition, it uses the `tkinter` library for visualizations, and `argparse` to read inputs, both of which come along with Python3. 

### Installation 

Assuming that Python3 is installed, ```numpy``` can be installed using ```pip```. 

```sh
pip install numpy
```

Alternatively, it can also be installed by running 
```sh
pip install -r requirements.txt
```

## Usage

The script can be run from the command line, by specifying the filename and the path to the object text file containing the the 3D object information. 

```sh
python polyhedron.py object.txt
```

## Implementation Details

The major functionality are set up in two classes -- `Polyhedron` and `Drawing` to develop the code. 

`Polyhedron` is the class containing all the information about the 3D Object such as it's vertices and faces. It also contains other additional utility methods to calculate the centroid, rotating about the x, y, z axes and reading from an input `.txt` file with the 3D object inputs. 

`Drawing` is the class containing all the methods regarding the `tkinter` canvas. It contains methods that control actions based on mouse inputs (such as click and drag), projection from 3D points to 2D canvas, and drawing the 3D object on the canvas.

`tkinter` is used to generate the wireframe plot and take mouse inputs to add the click and drag functionality. 

Initially, a 2D canvas is generated using `tkinter` and the 3D points from the input text file are used to instantiate a new `Polyhedron` and `Drawing` object. The 3D points are then projected onto the 2D canvas and a wireframe is generated for the user.  

The following algorithm is used find the shade for a particular face of the polyhedron:

1. First, find the surface normal of the face. This is done by taking the cross-product of two vectors generated using the vertices of the face (the cross-product of two vectors on a plane is a vector perpendicular to the plane).
2. Find the angle between the surface normal of the face and the vector of the positive z-axis. This can be done by taking the dot product between the two vectors ($\vec{a} \cdot \vec{b} = | \vec{a} | |\vec{b} | \cos{\theta} $). 
3. As mentioned in the requirements, we determine the shade of the face based on this angle -- i.e. if the surface normal is orthogonal to the z-axis, it is colored #00005F and varies smoothly till #0000FF when it is along the z-axis. 

To ensure that only the closest polyhedron faces are visible to the user (i.e. for visible surface determination), I used the [Painter's algorithm](https://en.wikipedia.org/wiki/Painter%27s_algorithm):

1. Calculate the centroid for each face of the polyhedron. 
2. Sort the faces based on the z-axis centroid depth
3. Place and shade the face from the furthest away face to the closest face to the user.

For click and drag functionality, I use 3D rotation matrices to rotate the object along the different axes, based on the rotation angle when the 3D object is clicked and dragged. This generates a new set of 3D vertices. These new vertices are then are then projected to the 2D canvas, and then drawn on the canvas to output the updated wireframe to the user. 
