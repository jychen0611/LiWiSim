import math
import random

# Room size
L = 10 # m
W = 10 # m
H = 3 # m

class Location():
    def generate_ue_location():
        x = random.uniform(0, L)  # x-coordinate in [0, 10)
        y = random.uniform(0, W)  # y-coordinate in [0, 10)
        return (x, y, 0)

    def generate_vlc_location():
        vlc_location = []
        for i in range(4):
            for j in range(4):
                x = 2*(i+1)
                y = 2*(j+1)
                z = H
                vlc_location.append((x, y, z))
        return vlc_location

    def geometric_distance(A, B):
        """
        Calculate the Euclidean distance between two 3D points.

        Parameters:
        A (tuple or list): Coordinates of the first point (x1, y1, z1)
        B (tuple or list): Coordinates of the second point (x2, y2, z2)

        Returns:
        float: Euclidean distance between p1 and p2
        """
        return math.sqrt((A[0] - B[0]) ** 2 +
                        (A[1] - B[1]) ** 2 +
                        (A[2] - B[2]) ** 2)