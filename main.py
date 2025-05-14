import config as cfg
from formula import Formula as f
from location import Location as l
from plot import Plot as p
from algorithm import Algorithm as a
import math
import random


def dbm_to_watts(P_dbm):
    """Convert power from dBm to Watts"""
    return 10**((P_dbm - 30) / 10)  # Since 1 mW = 10^(-3) W


if __name__ == "__main__":
    print("Simulation Start!")
    
    # Uniformly generate the location of each VLC AP/UE
    ue_locations = [l.generate_ue_location() for _ in range(cfg.N_UE)]
    vlc_locations = l.generate_vlc_location(cfg.N_VLC)
    # Define location of WiFi AP
    wifi_location = (5, 5, 3)

    # Calculate the geometric distance of each AP/UE pair
    distance = [[l.geometric_distance(ue_locations[i], vlc_locations[j]) for j in range(cfg.N_VLC)] for i in range(cfg.N_UE)]

    # Visualize LiWi Network 
    # p.plot_network_distribution(ue_locations, vlc_locations, wifi_location)
    p.plot_network_distribution_with_labels(ue_locations, vlc_locations, wifi_location)
    # Calculate the angle between each VLC AP/UE
    angle = [[l.calculate_angles(ue_locations[i], vlc_locations[j])[0] for j in range(cfg.N_VLC)] for i in range(cfg.N_UE)]
    # Calculate optical concenteator
    optical_concentrator = [[f.optical_concentrator(incident_angle=angle[i][j]) for j in range(cfg.N_VLC)] for i in range(cfg.N_UE)]

    # Generate the available VLC AP set of each UE
    K = []
    for i in range(cfg.N_UE):
        Ki = set()
        for j in range(cfg.N_VLC):
            if angle[i][j]<cfg.F_O_V:
                Ki.add(j)
        K.append(Ki)

    # Generate the servable UE set of each VLC AP
    H = []
    for j in range(cfg.N_VLC):
        Hj = set()
        for i in range(cfg.N_UE):
            if angle[i][j]<cfg.F_O_V:
                Hj.add(i)
        H.append(Hj)

    # Generate the required data rate (Mbps) of each UE
    rate_options = {10, 20, 40, 60, 80, 100}
    require_data_rate = [random.choice(list(rate_options)) for i in range(cfg.N_UE)]


    # Calculate VLC data rate based on R-band / G-band / B-band
    vlc_channel_gain = [[0 for j in range(cfg.N_VLC)] for i in range(cfg.N_UE)]
    vlc_sinr_R = [[0 for j in range(cfg.N_VLC)] for i in range(cfg.N_UE)]
    vlc_data_rate_R = [[0 for j in range(cfg.N_VLC)] for i in range(cfg.N_UE)]
    vlc_sinr_G = [[0 for j in range(cfg.N_VLC)] for i in range(cfg.N_UE)]
    vlc_data_rate_G = [[0 for j in range(cfg.N_VLC)] for i in range(cfg.N_UE)]
    vlc_sinr_B = [[0 for j in range(cfg.N_VLC)] for i in range(cfg.N_UE)]
    vlc_data_rate_B = [[0 for j in range(cfg.N_VLC)] for i in range(cfg.N_UE)]
    # For each UE
    for i in range(cfg.N_UE):
        # For each available AP of UE_i
        for j in K[i]:
            # Calculate channel gain
            vlc_channel_gain[i][j] = f.vlc_channel_gain(d = distance[i][j], irradiant_angle=angle[i][j], incident_angle=angle[i][j], optical_concentrator=optical_concentrator[i][j])
            # Calculate the inter-cell interference of R-band
            interference = 0
            P_ici = 0
            P_tx_watts = cfg.P_TX_VLC_R
            OE = cfg.R_OE
            for k in K[i]:
                if k==j:
                    continue 

                P_ici += OE*P_tx_watts*f.vlc_channel_gain(d = distance[i][k], irradiant_angle=angle[i][k], incident_angle=angle[i][k], optical_concentrator=optical_concentrator[i][k])
                interference += ((OE*P_tx_watts*f.vlc_channel_gain(d = distance[i][k], irradiant_angle=angle[i][k], incident_angle=angle[i][k], optical_concentrator=optical_concentrator[i][k])) ** 2 )
            # Calculate shot noise
            shot = f.shot_noise(P_sig=OE*P_tx_watts*vlc_channel_gain[i][j], P_ici=P_ici)
            # Calculate sinr
            vlc_sinr_R[i][j] = f.vlc_sinr(H_vlc=vlc_channel_gain[i][j], shot=shot, interference=interference, band=0)
            # Calculate data rate
            vlc_data_rate_R[i][j] = f.vlc_data_rate(sinr=vlc_sinr_R[i][j])

            # Calculate the inter-cell interference of G-band
            interference = 0
            P_ici = 0
            P_tx_watts = cfg.P_TX_VLC_G
            OE = cfg.G_OE
            for k in K[i]:
                if k==j:
                    continue 

                P_ici += OE*P_tx_watts*f.vlc_channel_gain(d = distance[i][k], irradiant_angle=angle[i][k], incident_angle=angle[i][k], optical_concentrator=optical_concentrator[i][k])
                interference += ((OE*P_tx_watts*f.vlc_channel_gain(d = distance[i][k], irradiant_angle=angle[i][k], incident_angle=angle[i][k], optical_concentrator=optical_concentrator[i][k])) ** 2 )
            # Calculate shot noise
            shot = f.shot_noise(P_sig=OE*P_tx_watts*vlc_channel_gain[i][j], P_ici=P_ici)
            # Calculate sinr
            vlc_sinr_G[i][j] = f.vlc_sinr(H_vlc=vlc_channel_gain[i][j], shot=shot, interference=interference, band=1)
            # Calculate data rate
            vlc_data_rate_G[i][j] = f.vlc_data_rate(sinr=vlc_sinr_G[i][j])

            # Calculate the inter-cell interference of B-band
            interference = 0
            P_ici = 0
            P_tx_watts = cfg.P_TX_VLC_B
            OE = cfg.B_OE
            for k in K[i]:
                if k==j:
                    continue 

                P_ici += OE*P_tx_watts*f.vlc_channel_gain(d = distance[i][k], irradiant_angle=angle[i][k], incident_angle=angle[i][k], optical_concentrator=optical_concentrator[i][k])
                interference += ((OE*P_tx_watts*f.vlc_channel_gain(d = distance[i][k], irradiant_angle=angle[i][k], incident_angle=angle[i][k], optical_concentrator=optical_concentrator[i][k])) ** 2 )
            # Calculate shot noise
            shot = f.shot_noise(P_sig=OE*P_tx_watts*vlc_channel_gain[i][j], P_ici=P_ici)
            # Calculate sinr
            vlc_sinr_B[i][j] = f.vlc_sinr(H_vlc=vlc_channel_gain[i][j], shot=shot, interference=interference, band=2)
            # Calculate data rate
            vlc_data_rate_B[i][j] = f.vlc_data_rate(sinr=vlc_sinr_B[i][j])
    
    vlc_data_rate = [vlc_data_rate_R, vlc_data_rate_G, vlc_data_rate_B]

    # print(vlc_channel_gain)
    p.plot_vlc_channel_gain_matrix(vlc_channel_gain)
    # print(vlc_sinr)
    p.plot_vlc_sinr_matrix(vlc_sinr_R)
    # print(vlc_data_rate)
    p.plot_vlc_data_rate_matrix(vlc_data_rate_R)

    



    [vlc_ap_selection_order, alpha]= a.VASIA(N_ue=cfg.N_UE, K=K, H=H, r=require_data_rate, distance=distance, angle=angle, optical_concentrator=optical_concentrator)
    # print(vlc_ap_selection_order)
    # print(alpha)
    ue_order = a.UPARU(N_ue=cfg.N_UE, K=K, H=H, r=require_data_rate, q=vlc_data_rate_R)
    # print(ue_order)
    [M, wifi, ue_allocation] = a.MCRAIC(N_ue=cfg.N_UE, N_vlc=cfg.N_VLC, U=ue_order, K=K, H=H, alpha=alpha, required_data_rate=require_data_rate, vlc_data_rate=vlc_data_rate)
    # p.plot_ue_allocation_2d_with_legend(ue_allocation)

    total_data_rate_of_each_ue = [0 for i in range(cfg.N_UE)]
    # Calculate total data rate obtained from VLC AP
    
    j = 0
    sum_rate = 0
    for m in M:
        total_data_rate_of_each_ue[m[0]] += vlc_data_rate_R[m[0]][j]
        total_data_rate_of_each_ue[m[1]] += vlc_data_rate_G[m[1]][j]
        total_data_rate_of_each_ue[m[2]] += vlc_data_rate_B[m[2]][j]
        sum_rate += (vlc_data_rate_R[m[0]][j] + vlc_data_rate_G[m[1]][j] + vlc_data_rate_B[m[0]][j])
        j += 1
    

    # wifi allocation #################################################################################
    wifi_channel_gain = [f.wifi_channel_gain(d=l.geometric_distance(ue_locations[i], wifi_location)) for i in range(cfg.N_UE)]
    p.plot_wifi_channel_gain_vector(wifi_channel_gain)
    wifi_snr = [f.wifi_snr(H_wifi=wifi_channel_gain[i], N_wifi_ue=len(wifi)) for i in range(cfg.N_UE)]
    p.plot_wifi_snr_vector(wifi_snr)
    wifi_data_rate = [f.wifi_data_rate(snr=wifi_snr[i], N_wifi_ue=len(wifi)) for i in range(cfg.N_UE)]
    p.plot_wifi_data_rate_vector(wifi_data_rate)

    # Calculate data rate obtained from WiFi 
    for w in wifi:
        total_data_rate_of_each_ue[w] += wifi_data_rate[w]
        sum_rate += wifi_data_rate[w]
    

    p.plot_total_data_rate(total_data_rate_of_each_ue=total_data_rate_of_each_ue, require_data_rate=require_data_rate)
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

