import config as cfg
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from typing import List



class Plot():

    def plot_network_distribution_with_labels(ue_locations, vlc_locations, wifi_location, fov_deg=cfg.F_O_V, ceiling_height=3.0):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Unpack coordinates
        ue_x, ue_y, ue_z = zip(*ue_locations)
        vlc_x, vlc_y, vlc_z = zip(*vlc_locations)
        wifi_x, wifi_y, wifi_z = wifi_location

        # Plot UE locations
        ax.scatter(ue_x, ue_y, ue_z, c='black', label='UE', marker='o')
        for idx, (x, y, z) in enumerate(ue_locations):
            ax.text(x, y, z + 0.05, f"UE{idx}", color='black', fontsize=8)

        # Plot VLC AP locations
        ax.scatter(vlc_x, vlc_y, vlc_z, c='orange', label='VLC AP', marker='^')
        for idx, (x, y, z) in enumerate(vlc_locations):
            ax.text(x, y, z + 0.05, f"VLC{idx}", color='darkorange', fontsize=8)

        # Plot WiFi AP location
        ax.scatter([wifi_x], [wifi_y], [wifi_z], c='red', label='WiFi AP', marker='s')
        ax.text(wifi_x, wifi_y, wifi_z + 0.05, "WiFi", color='red', fontsize=10)

        # Draw VLC FOV ground circles
        fov_rad = np.radians(fov_deg)
        radius = ceiling_height * np.tan(fov_rad)
        i=0
        for (x, y, z) in vlc_locations:
            if i == (int)(cfg.N_VLC/2):
                Plot.draw_vlc_fov_cone(ax, x, y, z, radius, ceiling_height)
            i += 1
    

        # Set room boundaries
        ax.set_xlim(0, cfg.L)
        ax.set_ylim(0, cfg.W)
        ax.set_zlim(0, cfg.H)

        # Labeling
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title('WiFi / LiFi / UE Distribution Diagram with VLC Ground Coverage and Labels')
        ax.legend()
        plt.show()

    def plot_network_distribution(ue_locations, vlc_locations, wifi_location, fov_deg=cfg.F_O_V, ceiling_height=3.0):
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
        ax.set_xlim(0, cfg.L)
        ax.set_ylim(0, cfg.W)
        ax.set_zlim(0, cfg.H)

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

    def plot_ue_allocation_2d_with_legend(alloc: List[set]) -> None:
        """
        Plots a 2D 5x5 rectangle diagram showing the VLC/WiFi allocation of each UE,
        with a color-coded legend and UE indices.

        Parameters:
            alloc: List of sets, where each set contains allocation codes for a UE.
                7 = WiFi, 0 = VLC R, 1 = VLC G, 2 = VLC B
        """
        if len(alloc) != 25:
            raise ValueError("Expected 25 UE allocations for a 5x5 grid.")

        fig, ax = plt.subplots(figsize=(6, 6))

        for idx, allocation in enumerate(alloc):
            row, col = divmod(idx, 5)

            # Determine RGB color
            r = 1.0 if 0 in allocation else 0.0
            g = 1.0 if 1 in allocation else 0.0
            b = 1.0 if 2 in allocation else 0.0

            color = [r, g, b]

            if allocation == {0}:
                label = 'VLC R'
            elif allocation == {1}:
                label = 'VLC G'
            elif allocation == {2}:
                label = 'VLC B'
            elif allocation == {0, 1}:
                label = 'VLC RG'
            elif allocation == {1, 2}:
                label = 'VLC GB'
            elif allocation == {0, 2}:
                label = 'VLC RB'
            elif allocation == {0, 1, 2}:
                label = 'VLC RGB'
            elif allocation == {7}:
                color = [1.0, 0.5, 1.0]
                label = 'WiFi'
            else:
                label = 'Mixed'

            rect = plt.Rectangle((col, 4 - row), 1, 1, facecolor=color, edgecolor='black')
            ax.add_patch(rect)
            ax.text(col + 0.5, 4 - row + 0.5, str(idx), ha='center', va='center', fontsize=8, color='black')

        ax.set_xlim(0, 5)
        ax.set_ylim(0, 5)
        ax.set_aspect('equal')
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title("2D UE Allocation Grid (RGB for VLC, Pink for WiFi)")

        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='red', edgecolor='black', label='VLC R'),
            Patch(facecolor='green', edgecolor='black', label='VLC G'),
            Patch(facecolor='blue', edgecolor='black', label='VLC B'),
            Patch(facecolor='yellow', edgecolor='black', label='VLC RG'),
            Patch(facecolor='cyan', edgecolor='black', label='VLC GB'),
            Patch(facecolor='magenta', edgecolor='black', label='VLC RB'),
            Patch(facecolor='white', edgecolor='black', label='VLC RGB'),
            Patch(facecolor=[1.0, 0.5, 1.0], edgecolor='black', label='WiFi')
        ]
        ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=4)

        plt.tight_layout()
        plt.show()

    '''
    def plot_total_data_rate(total_data_rate_of_each_ue: List[float], require_data_rate: List[float]) -> None:
        """
        Draws a bar chart of total/require data rate for each UE.

        Parameters:
            total_data_rate_of_each_ue: A list of total data rates (e.g., in Mbps) for each UE.
            require_data_rate: A list of required data rates (e.g., in Mbps) for each UE.
        """
        ue_ids = list(range(len(total_data_rate_of_each_ue)))

        plt.figure(figsize=(12, 4))
        plt.bar(ue_ids, total_data_rate_of_each_ue, color='skyblue', edgecolor='black')
        plt.bar(ue_ids, require_data_rate, color='orange', edgecolor='black')
        plt.xlabel('UE Index')
        plt.ylabel('Data Rate (Mbps)')
        plt.title('Total/Require Data Rate of Each UE')
        plt.xticks(ue_ids)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()
    '''
    def plot_total_data_rate(total_data_rate_of_each_ue: List[float], require_data_rate: List[float]) -> None:
        """
        Draws a grouped bar chart comparing total and required data rates for each UE.

        Parameters:
            total_data_rate_of_each_ue: A list of total data rates (e.g., in Mbps) for each UE.
            require_data_rate: A list of required data rates (e.g., in Mbps) for each UE.
        """
        ue_ids = np.arange(len(total_data_rate_of_each_ue))
        bar_width = 0.4

        plt.figure(figsize=(12, 4))
        plt.bar(ue_ids - bar_width / 2, total_data_rate_of_each_ue, width=bar_width,
                color='skyblue', edgecolor='black', label='Total Data Rate')
        plt.bar(ue_ids + bar_width / 2, require_data_rate, width=bar_width,
                color='brown', edgecolor='black', label='Required Data Rate')

        plt.xlabel('UE Index')
        plt.ylabel('Data Rate (Mbps)')
        plt.title('Total vs. Required Data Rate per UE')
        plt.xticks(ue_ids)
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    def plot_fov_vs_STP(avg_STP:List[float]):
        fov_range = list(range(30, 91, 5))
        # Plotting
        plt.figure()
        plt.plot(fov_range, avg_STP, marker='o')
        plt.title('FoV vs. System Throughput')
        plt.xlabel('Field of View (degrees)')
        plt.ylabel('System Throughput (Mbps)')
        plt.grid(True)
        # Set y-axis limits (adjust the values as needed)
        plt.ylim(bottom=0) 
        # Save figure to file
        plt.savefig('diagram/fov_vs_stp.png', dpi=300, bbox_inches='tight') 
        plt.show()

    def plot_fov_vs_AUS(avg_AUS:List[float]):
        fov_range = list(range(30, 91, 5))
        # Plotting
        plt.figure()
        plt.plot(fov_range, avg_AUS, marker='o')
        plt.title('FoV vs. AUS')
        plt.xlabel('Field of View (degrees)')
        plt.ylabel('Average User Satisfaction')
        plt.grid(True)
        # Set y-axis limits (adjust the values as needed)
        plt.ylim(0.1, 1)  
        # Save figure to file
        plt.savefig('diagram/fov_vs_aus.png', dpi=300, bbox_inches='tight')
        plt.show()

    def plot_fov_vs_SFI(avg_SFI:List[float]):
        fov_range = list(range(30, 91, 5))
        # Plotting
        plt.figure()
        plt.plot(fov_range, avg_SFI, marker='o')
        plt.title('FoV vs. SFI')
        plt.xlabel('Field of View (degrees)')
        plt.ylabel('Service Fairness Index')
        plt.grid(True)
        # Set y-axis limits (adjust the values as needed)
        plt.ylim(0.2, 1)  
        # Save figure to file
        plt.savefig('diagram/fov_vs_sfi.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_nue_vs_STP(avg_STP:List[float]):
        nue_range = list(range(1, 25, 1))
        # Plotting
        plt.figure()
        plt.plot(nue_range, avg_STP, marker='o')
        plt.title('N_UE vs. System Throughput')
        plt.xlabel('Number of UEs')
        plt.ylabel('System Throughput (Mbps)')
        plt.grid(True)
        # Set y-axis limits (adjust the values as needed)
        plt.ylim(bottom=0)  
        # Save figure to file
        plt.savefig('diagram/nue_vs_stp.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_nue_vs_AUS(avg_AUS:List[float]):
        nue_range = list(range(1, 25, 1))
        # Plotting
        plt.figure()
        plt.plot(nue_range, avg_AUS, marker='o')
        plt.title('N_UE vs. AUS')
        plt.xlabel('Number of UEs')
        plt.ylabel('Average User Satisfaction')
        plt.grid(True)
        # Set y-axis limits (adjust the values as needed)
        plt.ylim(0.3, 1)  
        # Save figure to file
        plt.savefig('diagram/nue_vs_aus.png', dpi=300, bbox_inches='tight')
        plt.show()

    def plot_nue_vs_SFI(avg_SFI:List[float]):
        nue_range = list(range(1, 25, 1))
        # Plotting
        plt.figure()
        plt.plot(nue_range, avg_SFI, marker='o')
        plt.title('N_UE vs. SFI')
        plt.xlabel('Number of UEs')
        plt.ylabel('Service Fairness Index')
        plt.grid(True)
        # Set y-axis limits (adjust the values as needed)
        plt.ylim(0.6, 1)  
        # Save figure to file
        plt.savefig('diagram/nue_vs_sfi.png', dpi=300, bbox_inches='tight')
        plt.show()