from formula import Formula as f
from location import Location as l
from plot import Plot as p
from algorithm import Algorithm as a
import math
# Room size
L = 10 # m
W = 10 # m
H = 3 # m
# Height of receiving plan
H_pd = 1.2 # m
# Transmit optical power per LED
P_vlc = 20 # W
# VLC system bandwidth
B_vlc = 20e6 # Hz
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
B_wifi = 20e6 # Hz
# Wifi noise spectral density
N_wifi = -174 # dBm/Hz
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
    ue_locations = [l.generate_ue_location() for _ in range(N_ue)]
    vlc_locations = l.generate_vlc_location()
    wifi_location = (5, 5, 3)
    # print(ue_locations[0])
    # print(vlc_locations[4])
    # print(wifi_location)
    # print(l.geometric_distance(ue_locations[0], vlc_locations[4]), l.geometric_distance(ue_locations[0], wifi_location)) 

    distance = [[l.geometric_distance(ue_locations[i], vlc_locations[j]) for j in range(N_vlc)] for i in range(N_ue)]
    # print(distance)
    # Visualize LiWi Network 
    #p.plot_network_distribution(ue_locations, vlc_locations, wifi_location)

    angle = [[l.calculate_angles(ue_locations[i], vlc_locations[j])[0] for j in range(N_vlc)] for i in range(N_ue)]
    optical_concentrator = [[f.optical_concentrator(incident_angle=angle[i][j]) for j in range(N_vlc)] for i in range(N_ue)]

    vlc_channel_gain = [[f.vlc_channel_gain(m=f.lambertian_emission_order(semi_angle_at_helf_power), A_pd=A_pd, d=distance[i][j], irradiant_angle=60, incident_angle=60, Fov=FoV, optical_filter_gain=optical_filter_gain, optical_concentrator=f.optical_concentrator(60, FoV)) for j in range(N_vlc)] for i in range(N_ue)]
    # print(vlc_channel_gain)
    #p.plot_vlc_channel_gain_matrix(vlc_channel_gain)

    total_channel_gain = []
    for j in range(N_vlc):
        total = 0
        for i in range(N_ue):
            total += vlc_channel_gain[i][j]
        total_channel_gain.append(total)
    # shot = f.shot_noise(P_sig=0.1, P_ici=0.1)
    # print(shot)
    thermal = f.thermal_noise()
    #print(thermal)
    vlc_sinr = [[f.vlc_sinr(oe_conversion=R_oe, P_vlc=P_vlc, H_vlc=vlc_channel_gain[i][j], shot=f.shot_noise(P_sig=R_oe*P_vlc*vlc_channel_gain[i][j], P_ici=R_oe*P_vlc*(total_channel_gain[j] - vlc_channel_gain[i][j])), thermal=thermal, interference=0.3) for j in range(N_vlc)] for i in range(N_ue)]
    # print(vlc_sinr)
    #p.plot_vlc_sinr_matrix(vlc_sinr)

    vlc_data_rate = [[f.vlc_data_rate(B_vlc=B_vlc, sinr=vlc_sinr[i][j]) for j in range(N_vlc)] for i in range(N_ue)]
    # print(vlc_data_rate)
    #p.plot_vlc_data_rate_matrix(vlc_data_rate)


    wifi_channel_gain = [f.wifi_channel_gain(h_r=f.generate_rayleigh_hr(), L_d=f.large_scale_fading_loss(l.geometric_distance(ue_locations[i], wifi_location))) for i in range(N_ue)]
    #p.plot_wifi_channel_gain_vector(wifi_channel_gain)

    wifi_snr = [f.wifi_snr(P_wifi=P_wifi, H_wifi=wifi_channel_gain[i], N_wifi=N_wifi, B_wifi=B_wifi) for i in range(N_ue)]
    #p.plot_wifi_snr_vector(wifi_snr)

    wifi_data_rate = [f.wifi_data_rate(B_wifi=B_wifi, snr=wifi_snr[i]) for i in range(N_ue)]
    #p.plot_wifi_data_rate_vector(wifi_data_rate)

    K = []
    for i in range(N_ue):
        Ki = set()
        for j in range(N_vlc):
            if optical_concentrator[i][j]>0:
                Ki.add(j)
        K.append(Ki)

    a.VASIA(N_ue=N_ue, K=K, distance=distance, angle=angle, optical_concentrator=optical_concentrator)



