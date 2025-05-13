from formula import Formula as f
from location import Location as l
from plot import Plot as p
from algorithm import Algorithm as a
import math
import random
# Room size
L = 10 # m
W = 10 # m
H = 3 # m
# Height of receiving plan
H_pd = 1.2 # m
# Transmit optical power per LED
P_vlc = 20 # W
# VLC system bandwidth
B_vlc = 20 # Hz
# Semi-angle at half power
semi_angle_at_helf_power = 60 # degree 
# Optical filter gain
optical_filter_gain = 1 
# Physical area of the PD
A_pd = 1 # cm^2
# O/E conversion coefficient
R_oe = 0.44 # A/W
G_oe = 0.23 # A/W
B_oe = 0.15 # A/W
# Wifi transmit power
P_wifi = 20 # dBm 
# Wifi bandwidth
B_wifi = 20 # MHz
# Wifi noise spectral density
Noise_wifi = -174 # dBm/Hz
# Wifi receiver power range
P_w_min = -125 # dBm
P_w_max = 50 # dBm
# PD light power range
P_v_min = 50 # uW
P_v_max = 10 # mW

# Number of VLC APs
N_vlc = 16
# Number of WiFi APs
N_wifi = 1
# Default number of UEs
N_ue = 25
# Default field of view angle of PD
FoV = 60 # degree




if __name__ == "__main__":
    print("Simulation Start!")
    
    # Uniformly generate the location of each VLC AP/UE
    ue_locations = [l.generate_ue_location() for _ in range(N_ue)]
    vlc_locations = l.generate_vlc_location()
    # Define location of WiFi AP
    wifi_location = (5, 5, 3)

    # Calculate the geometric distance of each AP/UE pair
    distance = [[l.geometric_distance(ue_locations[i], vlc_locations[j]) for j in range(N_vlc)] for i in range(N_ue)]

    # Visualize LiWi Network 
    # p.plot_network_distribution(ue_locations, vlc_locations, wifi_location)
    p.plot_network_distribution_with_labels(ue_locations, vlc_locations, wifi_location)
    # Calculate the angle between each VLC AP/UE
    angle = [[l.calculate_angles(ue_locations[i], vlc_locations[j])[0] for j in range(N_vlc)] for i in range(N_ue)]
    # Calculate optical concenteator
    optical_concentrator = [[f.optical_concentrator(incident_angle=angle[i][j]) for j in range(N_vlc)] for i in range(N_ue)]

    # Generate the available VLC AP set of each UE
    K = []
    for i in range(N_ue):
        Ki = set()
        for j in range(N_vlc):
            if angle[i][j]<40:
                Ki.add(j)
        K.append(Ki)

    # Generate the servable UE set of each VLC AP
    H = []
    for j in range(N_vlc):
        Hj = set()
        for i in range(N_ue):
            if angle[i][j]<40:
                Hj.add(i)
        H.append(Hj)

    # Generate the required data rate (Mbps) of each UE
    rate_options = {10, 20, 40, 60, 80, 100}
    r = [random.choice(list(rate_options)) for i in range(N_ue)]


    # Calculate VLC data rate based on R-band
    vlc_channel_gain = [[0 for j in range(N_vlc)] for i in range(N_ue)]
    vlc_sinr = [[0 for j in range(N_vlc)] for i in range(N_ue)]
    vlc_data_rate = [[0 for j in range(N_vlc)] for i in range(N_ue)]
    # For each UE
    for i in range(N_ue):
        # For each available AP of UE_i
        for j in K[i]:
            # Calculate channel gain
            vlc_channel_gain[i][j] = f.vlc_channel_gain(d = distance[i][j], irradiant_angle=angle[i][j], incident_angle=angle[i][j], optical_concentrator=optical_concentrator[i][j])
            # Calculate the inter-cell interference of this connection
            interference = 0
            P_ici = 0
            for k in K[i]:
                if k==j:
                    continue 
                P_ici += 0.44*6.66*f.vlc_channel_gain(d = distance[i][k], irradiant_angle=angle[i][k], incident_angle=angle[i][k], optical_concentrator=optical_concentrator[i][k])
                interference += ((0.44*6.66*f.vlc_channel_gain(d = distance[i][k], irradiant_angle=angle[i][k], incident_angle=angle[i][k], optical_concentrator=optical_concentrator[i][k])) ** 2 )
            # Calculate shot noise
            shot = f.shot_noise(P_sig=0.44*6.66*vlc_channel_gain[i][j], P_ici=P_ici)
            # Calculate sinr
            vlc_sinr[i][j] = f.vlc_sinr(H_vlc=vlc_channel_gain[i][j], shot=shot, interference=interference)
            # Calculate data rate
            vlc_data_rate[i][j] = f.vlc_data_rate(sinr=vlc_sinr[i][j])
    
    # print(vlc_channel_gain)
    # p.plot_vlc_channel_gain_matrix(vlc_channel_gain)
    # print(vlc_sinr)
    # p.plot_vlc_sinr_matrix(vlc_sinr)
    # print(vlc_data_rate)
    # p.plot_vlc_data_rate_matrix(vlc_data_rate)



    [vlc_ap_selection_order, alpha]= a.VASIA(N_ue=N_ue, K=K, H=H, r=r, distance=distance, angle=angle, optical_concentrator=optical_concentrator)
    # print(vlc_ap_selection_order)
    # print(alpha)
    ue_order = a.UPARU(N_ue=N_ue, K=K, H=H, r=r, q=vlc_data_rate)
    # print(ue_order)
    [M, wifi, ue_allocation] = a.MCRAIC(N_ue=N_ue, N_vlc=N_vlc, U=ue_order, K=K, H=H, alpha=alpha)
    # p.plot_ue_allocation_2d_with_legend(ue_allocation)

    total_data_rate_of_each_ue = [0 for i in range(N_ue)]
    # Calculate total data rate obtained from VLC AP
    
    j = 0
    sum_rate = 0
    for m in M:
        total_data_rate_of_each_ue[m[0]] += vlc_data_rate[m[0]][j]
        total_data_rate_of_each_ue[m[1]] += vlc_data_rate[m[1]][j]
        total_data_rate_of_each_ue[m[2]] += vlc_data_rate[m[2]][j]
        sum_rate += (vlc_data_rate[m[0]][j] + vlc_data_rate[m[1]][j] + vlc_data_rate[m[0]][j])
        j += 1
    
    # print("Sum rate: ", sum_rate)

    # wifi allocation #################################################################################
    wifi_channel_gain = [f.wifi_channel_gain(d=l.geometric_distance(ue_locations[i], wifi_location)) for i in range(N_ue)]
    p.plot_wifi_channel_gain_vector(wifi_channel_gain)
    wifi_snr = [f.wifi_snr(H_wifi=wifi_channel_gain[i], N_ue=len(wifi)) for i in range(N_ue)]
    p.plot_wifi_snr_vector(wifi_snr)
    wifi_data_rate = [f.wifi_data_rate(snr=wifi_snr[i], N_ue=len(wifi)) for i in range(N_ue)]
    p.plot_wifi_data_rate_vector(wifi_data_rate)

    # Calculate data rate obtained from WiFi 
    for w in wifi:
        total_data_rate_of_each_ue[w] += wifi_data_rate[w]
        sum_rate += wifi_data_rate[w]

    p.plot_total_data_rate(total_data_rate_of_each_ue)
    print("Sum rate: ", sum_rate)

    '''
    # wifi test
    c10 = f.wifi_channel_gain(d=10)
    c5 = f.wifi_channel_gain(d=10)
    c1 = f.wifi_channel_gain(d=10)
    s10 = f.wifi_snr(H_wifi=c10, N_ue=10)
    s5 = f.wifi_snr(H_wifi=c5, N_ue=10)
    s1 = f.wifi_snr(H_wifi=c1, N_ue=10)
    print("d=10")
    print("snr:", s10)
    print("data rate:", f.wifi_data_rate(snr=s10, N_ue=10))
    print("d=5")
    print("snr:", s5)
    print("data rate:", f.wifi_data_rate(snr=s5, N_ue=10))
    print("d=1")
    print("snr:", s1)
    print("data rate:", f.wifi_data_rate(snr=s1, N_ue=10))
    '''

