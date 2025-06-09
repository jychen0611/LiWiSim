import config as cfg
from formula import Formula as f
from location import Location as l
import random

def RANDOM(N_ue, N_vlc, K, required_data_rate, vlc_data_rate, ue_locations, wifi_location):
    # Set remain data rate requirement
    remained_data_rate = required_data_rate.copy()
    
    wifi = []
    lifi = []
    N_wifi_UE = 0
    for i in range(N_ue):
        # Random choice from a list (lifi: 0,2  wifi: 1)
        rd = random.choice([0, 1])
        if rd % 2 == 0:
            lifi.append(i)
        else:
            N_wifi_UE += 1
            wifi.append(i)

    STP = 0
    total_data_rate_of_each_ue = [0 for i in range(N_ue)]
    
    # The remaining band of each VLC AP
    C = [{0, 1, 2} for j in range(N_vlc)]

    for ue in lifi:
        for ap in K[ue]:
            while C[ap]:
                # assign an available band to UE-i;
                band = C[ap].pop()
                total_data_rate_of_each_ue[ue] += vlc_data_rate[band][ue][ap]
                # Update STP
                STP += vlc_data_rate[band][ue][ap]
                # Update the require data rate
                remained_data_rate[ue] -= vlc_data_rate[band][ue][ap]
                
                if remained_data_rate[ue] <= 0:
                    break
            
            if remained_data_rate[ue] <= 0:
                break

    # wifi allocation #################################################################################
    # Caculate the WiFi data rate of each UE
    wifi_channel_gain = [f.wifi_channel_gain(d=l.geometric_distance(ue_locations[i], wifi_location)) for i in range(N_ue)]
    # p.plot_wifi_channel_gain_vector(wifi_channel_gain)
    wifi_snr = [f.wifi_snr(H_wifi=wifi_channel_gain[i], N_wifi_ue=N_wifi_UE) for i in range(N_ue)]
    # p.plot_wifi_snr_vector(wifi_snr)
    wifi_data_rate = [f.wifi_data_rate(snr=wifi_snr[i], N_wifi_ue=N_wifi_UE) for i in range(N_ue)]
    #p.plot_wifi_data_rate_vector(wifi_data_rate)
    
    # Calculate data rate obtained from WiFi 
    for ue in wifi:
        total_data_rate_of_each_ue[ue] += wifi_data_rate[ue]
        STP += wifi_data_rate[ue]    


     # Caculate average user satisfaction (AUS)
    AUS = 0
    for i in range(N_ue):
        if total_data_rate_of_each_ue[i]/required_data_rate[i] > 1:
            AUS += 1
        else:
            AUS += total_data_rate_of_each_ue[i]/required_data_rate[i]
    AUS /= N_ue

    # Caculate Service Fairness Index (SFI)
    SFI = 0
    upper = 0
    lower = 0
    for i in range(N_ue):
        upper += total_data_rate_of_each_ue[i]
        lower += (total_data_rate_of_each_ue[i] ** 2)
    if lower != 0:
        SFI = (upper ** 2) / (N_ue * lower)    
    else:
        SFI = 0.5

    # Calculate User Satisfaction Rate (USR)
    USR = 0
    satisfied_ue = 0
    for i in range(N_ue):
        if total_data_rate_of_each_ue[i]/required_data_rate[i] >= 1:
            satisfied_ue += 1
    USR = satisfied_ue / N_ue

    return STP, AUS, SFI, USR

def RANDOM_EXE(N_UE, FoV):
    # Uniformly generate the location of each VLC AP/UE
    ue_locations = [l.generate_ue_location() for _ in range(N_UE)]
    vlc_locations = l.generate_vlc_location(cfg.N_VLC)
    # Define location of WiFi AP
    wifi_location = (5, 5, 3)

    # Calculate the geometric distance of each AP/UE pair
    distance = [[l.geometric_distance(ue_locations[i], vlc_locations[j]) for j in range(cfg.N_VLC)] for i in range(N_UE)]

    # Visualize LiWi Network 
    # p.plot_network_distribution(ue_locations, vlc_locations, wifi_location)
    # p.plot_network_distribution_with_labels(ue_locations, vlc_locations, wifi_location)
    # Calculate the angle between each VLC AP/UE
    angle = [[l.calculate_angles(ue_locations[i], vlc_locations[j])[0] for j in range(cfg.N_VLC)] for i in range(N_UE)]
    # Calculate optical concenteator
    optical_concentrator = [[f.optical_concentrator(incident_angle=angle[i][j], FoV=FoV) for j in range(cfg.N_VLC)] for i in range(N_UE)]

    # Generate the available VLC AP set of each UE
    K = []
    for i in range(N_UE):
        Ki = set()
        for j in range(cfg.N_VLC):
            if angle[i][j]<FoV:
                Ki.add(j)
        K.append(Ki)

    # Generate the servable UE set of each VLC AP
    H = []
    for j in range(cfg.N_VLC):
        Hj = set()
        for i in range(N_UE):
            if angle[i][j]<FoV:
                Hj.add(i)
        H.append(Hj)

    # Generate the required data rate (Mbps) of each UE
    rate_options = {10, 20, 40, 60, 80, 100}
    require_data_rate = [random.choice(list(rate_options)) for i in range(N_UE)]


    # Calculate VLC data rate based on R-band / G-band / B-band
    vlc_channel_gain = [[0 for j in range(cfg.N_VLC)] for i in range(N_UE)]
    vlc_sinr_R = [[0 for j in range(cfg.N_VLC)] for i in range(N_UE)]
    vlc_data_rate_R = [[0 for j in range(cfg.N_VLC)] for i in range(N_UE)]
    vlc_sinr_G = [[0 for j in range(cfg.N_VLC)] for i in range(N_UE)]
    vlc_data_rate_G = [[0 for j in range(cfg.N_VLC)] for i in range(N_UE)]
    vlc_sinr_B = [[0 for j in range(cfg.N_VLC)] for i in range(N_UE)]
    vlc_data_rate_B = [[0 for j in range(cfg.N_VLC)] for i in range(N_UE)]
    # For each UE
    for i in range(N_UE):
        # For each available AP of UE_i
        for j in K[i]:
            # Calculate channel gain
            vlc_channel_gain[i][j] = f.vlc_channel_gain(d = distance[i][j], irradiant_angle=angle[i][j], incident_angle=angle[i][j], optical_concentrator=optical_concentrator[i][j], FoV=FoV)
            # Calculate the inter-cell interference of R-band
            interference = 0
            P_ici = 0
            P_tx_watts = cfg.P_TX_VLC_R
            OE = cfg.R_OE
            for k in K[i]:
                if k==j:
                    continue 

                P_ici += OE*P_tx_watts*f.vlc_channel_gain(d = distance[i][k], irradiant_angle=angle[i][k], incident_angle=angle[i][k], optical_concentrator=optical_concentrator[i][k], FoV=FoV)
                interference += ((OE*P_tx_watts*f.vlc_channel_gain(d = distance[i][k], irradiant_angle=angle[i][k], incident_angle=angle[i][k], optical_concentrator=optical_concentrator[i][k], FoV=FoV)) ** 2 )
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

                P_ici += OE*P_tx_watts*f.vlc_channel_gain(d = distance[i][k], irradiant_angle=angle[i][k], incident_angle=angle[i][k], optical_concentrator=optical_concentrator[i][k], FoV=FoV)
                interference += ((OE*P_tx_watts*f.vlc_channel_gain(d = distance[i][k], irradiant_angle=angle[i][k], incident_angle=angle[i][k], optical_concentrator=optical_concentrator[i][k], FoV=FoV)) ** 2 )
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

                P_ici += OE*P_tx_watts*f.vlc_channel_gain(d = distance[i][k], irradiant_angle=angle[i][k], incident_angle=angle[i][k], optical_concentrator=optical_concentrator[i][k], FoV=FoV)
                interference += ((OE*P_tx_watts*f.vlc_channel_gain(d = distance[i][k], irradiant_angle=angle[i][k], incident_angle=angle[i][k], optical_concentrator=optical_concentrator[i][k], FoV=FoV)) ** 2 )
            # Calculate shot noise
            shot = f.shot_noise(P_sig=OE*P_tx_watts*vlc_channel_gain[i][j], P_ici=P_ici)
            # Calculate sinr
            vlc_sinr_B[i][j] = f.vlc_sinr(H_vlc=vlc_channel_gain[i][j], shot=shot, interference=interference, band=2)
            # Calculate data rate
            vlc_data_rate_B[i][j] = f.vlc_data_rate(sinr=vlc_sinr_B[i][j])
    
    vlc_data_rate = [vlc_data_rate_R, vlc_data_rate_G, vlc_data_rate_B]

        


    [STP, AUS, SFI, USR] = RANDOM(N_ue=N_UE, N_vlc=cfg.N_VLC, K=K, required_data_rate=require_data_rate, vlc_data_rate=vlc_data_rate, ue_locations=ue_locations, wifi_location=wifi_location)
    return STP, AUS, SFI, USR