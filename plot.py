import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

class Plot():
    def plot_network_distribution(ue_locations, vlc_locations, wifi_location, fov_deg=60, ceiling_height=3.0):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Unpack coordinates
        ue_x, ue_y, ue_z = zip(*ue_locations)
        vlc_x, vlc_y, vlc_z = zip(*vlc_locations)
        wifi_x, wifi_y, wifi_z = wifi_location

        # Plot UE locations
        ax.scatter(ue_x, ue_y, ue_z, c='black', label='UE', marker='o')

        # Plot VLC AP locations
        ax.scatter(vlc_x, vlc_y, vlc_z, c='orange', label='VLC AP', marker='^')

        # Plot WiFi AP location
        ax.scatter([wifi_x], [wifi_y], [wifi_z], c='red', label='WiFi AP', marker='s')

        # Draw VLC FOV ground circles
        fov_rad = np.radians(fov_deg)
        radius = ceiling_height * np.tan(fov_rad)

        for (x, y, z) in vlc_locations:
            if x == 6 and y == 6:
                Plot.draw_vlc_fov_cone(ax, x, y, z, radius, ceiling_height)
                #Plot.draw_vlc_ground_circle(ax, x, y, radius)

        # Set room boundaries
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_zlim(0, 3)

        # Labeling
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title('WiFi / LiFi / UE Distribution Diagram with VLC Ground Coverage')
        ax.legend()
        plt.show()

    # Ground circle drawer
    def draw_vlc_ground_circle(ax, x0, y0, radius, resolution=100):
        theta = np.linspace(0, 2 * np.pi, resolution)
        circle_x = x0 + radius * np.cos(theta)
        circle_y = y0 + radius * np.sin(theta)
        circle_z = np.zeros_like(circle_x)  # On the ground (z = 0)

        ax.plot(circle_x, circle_y, circle_z, color='orange', alpha=0.5, linestyle='-')

    def draw_vlc_fov_cone(ax, x0, y0, z0, radius, height, resolution=30):
        # Generate circle base of the cone
        theta = np.linspace(0, 2 * np.pi, resolution)
        circle_x = radius * np.cos(theta) + x0
        circle_y = radius * np.sin(theta) + y0
        circle_z = np.full_like(circle_x, z0 - height)

        # Draw cone sides
        for i in range(len(theta)):
            ax.plot([x0, circle_x[i]], [y0, circle_y[i]], [z0, circle_z[i]], color='orange', alpha=0.2)

        # Draw the circular base
        ax.plot_trisurf(circle_x, circle_y, circle_z, color='orange', alpha=0.1)

    '''

    def plot_network_distribution(ue_locations, vlc_locations, wifi_location):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Unpack coordinates
        ue_x, ue_y, ue_z = zip(*ue_locations)
        vlc_x, vlc_y, vlc_z = zip(*vlc_locations)
        wifi_x, wifi_y, wifi_z = wifi_location

        # Plot UE locations
        ax.scatter(ue_x, ue_y, ue_z, c='blue', label='UE', marker='o')

        # Plot VLC AP locations
        ax.scatter(vlc_x, vlc_y, vlc_z, c='green', label='VLC AP', marker='^')

        # Plot WiFi AP location
        ax.scatter([wifi_x], [wifi_y], [wifi_z], c='red', label='WiFi AP', marker='s')

        # Labeling
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('WiFi / LiFi / UE Distribution Diagram')
        ax.legend()
        plt.show()
    '''
    def plot_vlc_channel_gain_matrix(channel_gain_matrix):
        """
        Plot the VLC channel gain matrix using only matplotlib.
        
        Parameters:
        - channel_gain_matrix: 2D list or NumPy array (N_ue × N_vlc)
        """
        gain_array = np.array(channel_gain_matrix)

        plt.figure(figsize=(10, 6))
        im = plt.imshow(gain_array, aspect='auto', cmap='YlGnBu')

        # Add color bar
        cbar = plt.colorbar(im)
        cbar.set_label("Channel Gain")

        # Add axis labels
        plt.xlabel("VLC Access Point Index")
        plt.ylabel("UE Index")
        plt.title("Channel Gain Distribution (UE ↔ VLC AP)")

        # Add value annotations (optional, can remove if too cluttered)
        for i in range(gain_array.shape[0]):
            for j in range(gain_array.shape[1]):
                plt.text(j, i, f"{gain_array[i, j]:.1e}", ha='center', va='center', fontsize=7)

        plt.tight_layout()
        plt.show()

    def plot_vlc_sinr_matrix(sinr_matrix):
        """
        Plot the SINR values between each UE and each VLC AP using matplotlib.

        Parameters:
        - sinr_matrix: 2D list or NumPy array (N_ue × N_vlc)
        """
        sinr_array = np.array(sinr_matrix)

        plt.figure(figsize=(10, 6))
        im = plt.imshow(sinr_array, aspect='auto', cmap='plasma')

        # Colorbar
        cbar = plt.colorbar(im)
        cbar.set_label("SINR")

        # Axis labels
        plt.xlabel("VLC Access Point Index")
        plt.ylabel("UE Index")
        plt.title("SINR Distribution (UE ↔ VLC AP)")

        # Optional: display SINR values in each cell
        for i in range(sinr_array.shape[0]):
            for j in range(sinr_array.shape[1]):
                plt.text(j, i, f"{sinr_array[i, j]:.2f}", ha='center', va='center', fontsize=7)

        plt.tight_layout()
        plt.show()

    def plot_vlc_data_rate_matrix(data_rate_matrix):
        """
        Plot the data rate between each UE and each VLC AP using matplotlib.

        Parameters:
        - data_rate_matrix: 2D list or NumPy array (N_ue × N_vlc), unit assumed to be in Mbps or Gbps.
        """
        data_rate_array = np.array(data_rate_matrix)

        plt.figure(figsize=(10, 6))
        im = plt.imshow(data_rate_array, aspect='auto', cmap='cividis')

        # Colorbar
        cbar = plt.colorbar(im)
        cbar.set_label("Data Rate (Mbps)")

        # Axis labels
        plt.xlabel("VLC Access Point Index")
        plt.ylabel("UE Index")
        plt.title("Data Rate Distribution (UE ↔ VLC AP)")

        # Optional: annotate each cell with data rate
        for i in range(data_rate_array.shape[0]):
            for j in range(data_rate_array.shape[1]):
                plt.text(j, i, f"{data_rate_array[i, j]:.2f}", ha='center', va='center', fontsize=7)

        plt.tight_layout()
        plt.show()
    
    def plot_wifi_channel_gain_vector(wifi_channel_gain):
        """
        Plot WiFi channel gain from the AP to each UE using the given gain vector.

        Parameters:
        - wifi_channel_gain: list or 1D array of channel gains for each UE
        """
        wifi_channel_gain = np.array(wifi_channel_gain)
        N_ue = len(wifi_channel_gain)

        plt.figure(figsize=(10, 5))
        plt.plot(range(N_ue), wifi_channel_gain, marker='o', linestyle='-', color='darkgreen')
        plt.xlabel("UE Index")
        plt.ylabel("Channel Gain")
        plt.title("WiFi Channel Gain to Each UE")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_wifi_snr_vector(wifi_snr):
        """
        Plot WiFi SNR from the AP to each UE.

        Parameters:
        - wifi_snr: list or 1D array of SNR values (can be in linear or dB)
        """
        wifi_snr = np.array(wifi_snr)
        N_ue = len(wifi_snr)

        plt.figure(figsize=(10, 5))
        plt.plot(range(N_ue), wifi_snr, marker='o', linestyle='-', color='darkorange')
        plt.xlabel("UE Index")
        plt.ylabel("WiFi SNR (dB)")
        plt.title("WiFi SNR for Each UE")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_wifi_data_rate_vector(wifi_data_rate):
        """
        Plot the WiFi data rate to each UE.

        Parameters:
        - wifi_data_rate: list or 1D array of data rates (e.g., Mbps or Gbps)
        """
        wifi_data_rate = np.array(wifi_data_rate)
        N_ue = len(wifi_data_rate)

        plt.figure(figsize=(10, 5))
        plt.plot(range(N_ue), wifi_data_rate, marker='o', linestyle='-', color='mediumblue')
        plt.xlabel("UE Index")
        plt.ylabel("WiFi Data Rate (Mbps)")
        plt.title("WiFi Data Rate for Each UE")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
