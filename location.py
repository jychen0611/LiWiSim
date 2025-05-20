import config as cfg
import math
import random
import numpy as np
import json



class Location():
    def generate_ue_location():
        x = random.uniform(0, cfg.L)  # x-coordinate in [0, 10)
        y = random.uniform(0, cfg.W)  # y-coordinate in [0, 10)
        return (x, y, cfg.H_PD)

    def generate_ue_locations_dataset(N, filename="ue_locations.json"):
        ue_locations = []

        for _ in range(N):
            x = random.uniform(0, cfg.L)
            y = random.uniform(0, cfg.W)
            z = cfg.H_PD
            ue_locations.append({"x": x, "y": y, "z": z})

        with open(filename, "w") as f:
            json.dump(ue_locations, f, indent=4)

        print(f"{N} UE locations saved to '{filename}'.")

    def load_ue_locations(filename="ue_locations.json"):
        with open(filename, "r") as f:
            ue_data = json.load(f)

        locations = [(ue["x"], ue["y"], ue["z"]) for ue in ue_data]
        return locations


    def move_ue_positions(ue_positions, step_size=0.001, room_bounds=(cfg.L, cfg.W)):
        """
        Simulate UE mobility by slightly modifying x, y coordinates.
        
        Parameters:
            ue_positions: List of current UE positions, shape (N_UE, 3)
                        Each element is [x, y, z]
            step_size: Max random step size for x and y (default: 0.1 meters)
            room_bounds: Tuple (x_max, y_max), the bounds of the room (in meters)
            
        Returns:
            Updated list of UE positions with same z, modified x, y
        """
        new_positions = []
        x_max, y_max = room_bounds

        for pos in ue_positions:
            x, y, z = pos
            dx = np.random.uniform(-step_size, step_size)
            dy = np.random.uniform(-step_size, step_size)
            new_x = np.clip(x + dx, 0, x_max)
            new_y = np.clip(y + dy, 0, y_max)
            new_positions.append([new_x, new_y, z])
        
        return new_positions


    def generate_vlc_location(N_vlc: int):
        if N_vlc == 1:
            return [(cfg.L/2, cfg.W/2, cfg.H)]
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