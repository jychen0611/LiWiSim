import config as cfg
import math
import random



class Location():
    def generate_ue_location():
        x = random.uniform(0, cfg.L)  # x-coordinate in [0, 10)
        y = random.uniform(0, cfg.W)  # y-coordinate in [0, 10)
        return (x, y, cfg.H_PD)

    def generate_vlc_location(N_vlc: int):
        vlc_location = []
        for i in range((int)(math.sqrt(N_vlc))):
            for j in range((int)(math.sqrt(N_vlc))):
                x = (cfg.L/(math.sqrt(N_vlc)-1))*(i)
                y = (cfg.W/(math.sqrt(N_vlc)-1))*(j)
                z = cfg.H
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
    
    def calculate_angles(rx_pos, tx_pos):
        # Vector from transmitter to receiver
        vec = [rx_pos[i] - tx_pos[i] for i in range(3)]
        
        # Normalize vector
        dist = math.sqrt(sum(v**2 for v in vec))
        vec_norm = [v / dist for v in vec]

        # LED facing downward
        tx_normal = [0, 0, -1]
        # UE facing upward
        rx_normal = [0, 0, 1]

        # Irradiance angle φ: angle between tx normal and vec
        cos_phi = sum(tx_normal[i] * vec_norm[i] for i in range(3))
        phi = math.degrees(math.acos(cos_phi))

        # Incidence angle θ: angle between rx normal and -vec
        cos_theta = sum(rx_normal[i] * (-vec_norm[i]) for i in range(3))
        theta = math.degrees(math.acos(cos_theta))

        return phi, theta