#!/usr/bin/env python3

import argparse
from tkinter import Canvas, Event, IntVar, Tk

import numpy as np


class Polyhedron:
    """
    Class for the Polyhedron 3D Object. Contains all the information about the 3D Object
    such as it's vertices and faces. Also contains additional utility methods to
    calculate the centroid, rotating about the x, y, z axes and reading from an input
    `.txt` file with the 3D object inputs.
    """

    def __init__(self) -> None:
        """
        Initializes the Polyhedron object with empty values for its number of vertices,
        number of faces, vertices, and faces.
        """
        self.num_vertices = 0
        self.num_faces = 0
        self.vertices = np.array([])
        self.faces = []

    def read_file(self, obj_text_file: str) -> None:
        """
        Reads a text file containing the definition of a polyhedron object, and
        initializes the Polyhedron object's values based on the file.
        Args:
            obj_text_file (str): A string containing the file path to the text file that
        defines the polyhedron object.
        """
        with open(obj_text_file) as f:
            first_line = f.readline().split(",")
            self.num_vertices = int(first_line[0])
            self.num_faces = int(first_line[1])
            self.vertices = np.zeros((self.num_vertices, 3), dtype=float)
            for _ in range(self.num_vertices):
                id, x, y, z = f.readline().split(",")
                # use (id-1) instead of id to change from 1-indexed to 0-indexed
                self.vertices[int(id) - 1] = np.array([float(x), float(y), float(z)])
            for _ in range(self.num_faces):
                vertices = f.readline().split(",")
                # use (id-1) instead of id to change from 1-indexed to 0-indexed
                vertices = [int(v) - 1 for v in vertices]
                self.faces.append(tuple(vertices))

    def calculate_centroid(self, face: list[float]) -> tuple:
        """
        Function to calculate centroid of a face of the polyhedron.

        Args:
            face (tuple): Tuple of vertices of the face

        Returns:
            list[float]: Centroid of the face
        """
        x, y, z = 0, 0, 0
        for vertex in face:
            x += self.vertices[vertex][0]
            y += self.vertices[vertex][1]
            z += self.vertices[vertex][2]
        x /= len(face)
        y /= len(face)
        z /= len(face)
        return [x, y, z]

    def rotate_x(self, angle: float) -> None:
        """
        Rotates the polyhedron object by a given angle around the x-axis, by applying
        a rotation matrix to the vertices.

        Args:
            angle (float): An integer representing the angle of rotation in degrees.
        """
        rotation_matrix = np.array(
            [
                [1, 0, 0],
                [0, np.cos(angle), -np.sin(angle)],
                [0, np.sin(angle), np.cos(angle)],
            ]
        )
        self.vertices = np.dot(self.vertices, rotation_matrix)

    def rotate_y(self, angle: float) -> None:
        """
        Rotates the polyhedron object by a given angle around the y-axis, by applying
        a rotation matrix to the vertices.

        Args:
            angle (float): An integer representing the angle of rotation in degrees.
        """
        rotation_matrix = np.array(
            [
                [np.cos(angle), 0, np.sin(angle)],
                [0, 1, 0],
                [-np.sin(angle), 0, np.cos(angle)],
            ]
        )
        self.vertices = np.dot(self.vertices, rotation_matrix)

    def rotate_z(self, angle: float) -> None:
        """
        Rotates the polyhedron object by a given angle around the z-axis, by applying
        a rotation matrix to the vertices.

        Args:
            angle (float): An integer representing the angle of rotation in degrees.
        """
        rotation_matrix = np.array(
            [
                [np.cos(angle), -np.sin(angle), 0],
                [np.sin(angle), np.cos(angle), 0],
                [0, 0, 1],
            ]
        )
        self.vertices = np.dot(self.vertices, rotation_matrix)


class Drawing:
    """
    Class containing all the methods regarding the `tkinter` canvas. Contains methods
    that control actions based on mouse inputs (such as click and drag), projection
    from 3D points to 2D canvas, and drawing the 3D object on the canvas.
    """

    def __init__(self, root: Tk, width: int, height: int) -> None:
        """
        Initialize a Drawing object with a Tkinter root, a width and a height

        Args:
            root (Tk): Tk class instance
            width (int): width of the canvas in pixels
            height (int): height of the canvas in pixels
        """
        self.root = root
        self.canvas = Canvas(self.root, width=width, height=height, background="white")
        self.canvas.pack()
        self.root.update()
        self.distance = IntVar()
        self.origin = [self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2]
        self.start_x, self.start_y = 0, 0
        self.bind_mouse_actions()

    def project(self, vertex: np.array, scaling_factor: int) -> tuple:
        """
        Project a vertex onto a 2D plane

        Args:
            vertex (np.array): numpy array of shape (3,) representing the coordinates
            of the vertex
            scaling_factor (int): scaling factor to adjust the size of the projection

        Returns:
            tuple: projected vertices on 2D canvas
        """
        x, y, z = vertex
        x = self.origin[0] + (x * scaling_factor)
        y = self.origin[1] + (y * scaling_factor)
        return x, y

    def draw_polyhedron(self, polyhedron: Polyhedron) -> None:
        """
        Draw and shade a Polyhedron object onto the canvas.

        The following algorithm is used find the shade for a particular face of the
        polyhedron:
        - First, find the surface normal of the face. This is done by taking the
        cross-product of two vectors generated using the vertices of the face (the
        cross-product of two vectors on a plane is a vector perpendicular to the plane).
        - Find the angle between the surface normal of the face and the vector of the
        positive z-axis. This can be done by taking the dot product between the two
        vectors.
        - As mentioned in the requirements, determine the shade of the face based
        on this angle -- i.e. if the surface normal is orthogonal to the z-axis, it is
        colored #00005F and varies smoothly till #0000FF when it is along the z-axis.

        To ensure that only the closest polyhedron faces are visible to the user
        (i.e. for visible surface determination), use Painter's Algorithm

        - Calculate the centroid for each face of the polyhedron.
        - Sort the faces based on the z-axis centroid depth
        - Place and shade the face from the furthest away face to the closest face
        to the user.

        Args:
            polyhedron (Polyhedron): Polyhedron object to be drawn
        """
        scaling_factor = self.origin[1] / 2  # object must fill half the window
        self.polyhedron = polyhedron
        z_ordered_faces = []
        r_min, g_min, b_min = self.canvas.winfo_rgb("#00005F")
        r_max, g_max, b_max = self.canvas.winfo_rgb("#0000FF")

        for face in polyhedron.faces:
            # Find the surface normal using cross product
            normal = np.cross(
                self.polyhedron.vertices[face[1]] - self.polyhedron.vertices[face[0]],
                self.polyhedron.vertices[face[2]] - self.polyhedron.vertices[face[1]],
            )
            normal = normal / np.linalg.norm(normal)
            # Generate shade between #00005F and #0000FF, based on angle with z-axis
            angle = np.dot(normal, np.array([0, 0, 1]))
            angle = np.arccos(np.clip(angle, -1, 1))
            if angle > np.pi / 2:  # clip angles to be between 0 and pi/2
                angle = np.pi - angle
            angle = np.pi / 2 - angle
            r = int(r_min + (r_max - r_min) * angle / (np.pi / 2))
            g = int(g_min + (g_max - g_min) * angle / (np.pi / 2))
            b = int(b_min + (b_max - b_min) * angle / (np.pi / 2))
            color = f"#{r:04x}{g:04x}{b:04x}"
            z_centroid = self.polyhedron.calculate_centroid(face)[2]
            z_ordered_faces.append((z_centroid, face, color))
        # Sort the faces based on how close they are to the viewer
        z_ordered_faces.sort(reverse=True)
        for _, face, color in z_ordered_faces:
            coords = [
                self.project(polyhedron.vertices[vertex], scaling_factor)
                for vertex in face
            ]
            for coord in coords:
                self.canvas.create_oval(
                    coord[0] - 5,
                    coord[1] - 5,
                    coord[0] + 5,
                    coord[1] + 5,
                    outline="blue",
                    fill="blue",
                    width=5,
                )
            self.canvas.create_polygon(coords, fill=color, outline=color, width=2)

    def bind_mouse_actions(self) -> None:
        """
        Bind the mouse actions to callback functions for Tkinter.
        """
        self.canvas.bind("<Button-1>", self.mouse_click)
        self.canvas.bind("<B1-Motion>", self.mouse_drag)

    def mouse_click(self, event: Event) -> None:
        """
        Event triggered on click

        Args:
            event (Event): Tkinter Event Object
        """
        self.start_x = event.x
        self.start_y = event.y

    def mouse_drag(self, event: Event) -> None:
        """
        Event triggered on drag

        Args:
            event (Event): Tkinter Event Object
        """
        x, y = event.x, event.y
        dx, dy = self.start_x - x, self.start_y - y
        self.polyhedron.rotate_x(dy * 0.001)
        self.polyhedron.rotate_y(-dx * 0.001)
        self.canvas.delete("all")
        self.draw_polyhedron(self.polyhedron)
        self.start_x, self.start_y = x, y


def main():
    """
    Main Function for the Polyhedron and Drawing classes
    """
    # read the input file
    parser = argparse.ArgumentParser(description="Polyhedron Visualization")
    parser.add_argument("obj_filename", type=str, help="Sample object file name")
    args = parser.parse_args()
    # instantiate polyhedron
    polyhedron = Polyhedron()
    polyhedron.read_file(args.obj_filename)
    # set up tkinter
    root = Tk()
    height = root.winfo_screenheight()
    width = root.winfo_screenwidth()
    # Set up Tkinter Drawing
    drawing = Drawing(root, width, height)
    drawing.draw_polyhedron(polyhedron)
    root.title("Polyhedron Visualization")
    root.mainloop()


if __name__ == "__main__":
    main()
