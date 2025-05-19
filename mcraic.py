import config as cfg
from typing import List, Set, Tuple
from formula import Formula as f
from location import Location as l
from plot import Plot as p

import random

def VASIA(N_ue:int, K:List[Set[int]], H:List[Set[int]], r:List[float], distance:List[List[float]], angle:List[List[float]], optical_concentrator:List[List[float]], FoV:float) -> Tuple[List[List[int]], List[List[float]]]:

    N_ap = 16
    # positive influence
    q = [[0 for j in range(N_ap)] for i in range(N_ue)]
    # primary UE set
    Y = [[set() for j in range(N_ap)] for i in range(N_ue)]
    Z = [[set() for j in range(N_ap)] for i in range(N_ue)]
    V = [[0 for j in range(N_ap)] for i in range(N_ue)]
    alpha = [[0 for j in range(N_ap)] for i in range(N_ue)]
    # The VLC AP selection order of each UE
    vlc_ap_selection_order = [[] for _ in range(N_ue)]
    # Calculate the positive influence of each connection
    for i in range(N_ue):
        for j in K[i]:
            # Calculate q_ij by equation (9)
            H_vlc = f.vlc_channel_gain(d = distance[i][j], irradiant_angle=angle[i][j], incident_angle=angle[i][j], optical_concentrator=optical_concentrator[i][j], FoV=FoV)
            interference = 0
            P_ici = 0
            P_tx_watts = cfg.P_TX_VLC_R
            for k in K[i]:
                if k==j:
                    continue 
                P_ici += 0.44*P_tx_watts*f.vlc_channel_gain(d = distance[i][k], irradiant_angle=angle[i][k], incident_angle=angle[i][k], optical_concentrator=optical_concentrator[i][k], FoV=FoV)
                interference += (0.44*P_tx_watts*f.vlc_channel_gain(d = distance[i][k], irradiant_angle=angle[i][k], incident_angle=angle[i][k], optical_concentrator=optical_concentrator[i][k], FoV=FoV)) ** 2 
            shot = f.shot_noise(P_sig=0.44*P_tx_watts*H_vlc, P_ici=P_ici)
            sinr = f.vlc_sinr(H_vlc=H_vlc, shot=shot, interference=interference, band=0)
            q[i][j] = f.vlc_data_rate(sinr=sinr)

    for i in range(N_ue):
        tmp = []
        for j in K[i]:
            # Generate the primary UE set Y_ij 
            Y[i][j] = H[j] - {i}
            # print("Primary ", i, j, " : ", Y[i][j])

            V_kij = [0 for _ in range(N_ue)] 
            for k in Y[i][j]:
                # Calculate v_k_ij by equation (10)
                # Calculate V_k_ij by equation (11)
                V_k_ij = 0
                for l in K[k]:
                    V_k_ij += q[k][l] * ((r[k]-5)/(100-10))
                V_kij[k] = V_k_ij
            # end for
        
            # Generate secondary UE set Z_ij by equation (12)
            Z[i][j] = set()
            for l in K[i]:
                if l == j:
                    continue
                Z[i][j] = Z[i][j] | H[l]
            Z[i][j] = Z[i][j] - H[j]
            # print("Secondary ", i, j, " : ", Z[i][j])

            V_lij = [0 for _ in range(N_ue)] 
            for l in Z[i][j]:
                # Calculate v_l_ij by equation (13) 
                # Calculate V_l_ij by equation (14)
                V_l_ij = 0
                for k in (K[l] & K[i]):
                    V_l_ij += q[l][k] * ((r[l]-5)/(100-10))
                V_lij[l] = V_l_ij
            # end for

            # Calculate V_ij by equation (15)
            V[i][j] = 0
            for k in Y[i][j]:
                V[i][j] += V_kij[k]
            for l in Z[i][j]:
                V[i][j] += V_lij[l]
            # Calculate alpha_ij by equation (16)
            alpha[i][j] = V[i][j]/q[i][j]
            
            # print("V: ", i, j, V[i][j])
            # print("alpha: ", i, j, alpha[i][j])
            tmp.append([j, alpha[i][j]])
        # end for

        # Generate the VLC AP selection order of UE_i by the order of alpha_ij from small to large.
        # Sort VLC order by alpha 
        vlc_order = [ap_idx for ap_idx, alpha in sorted(tmp, key=lambda x: x[1])]
        vlc_ap_selection_order[i] = vlc_order
        # print("vlc_ap_selection_order: ", i, vlc_ap_selection_order[i])
    # end for
    # p.plot_vlc_data_rate_matrix(q)
    return vlc_ap_selection_order, alpha

def UPARU(N_ue:int, K:List[Set[int]], H:List[Set[int]], r:List[float], q:List[List[float]]):
    # Initialize the priority factor of each UE to zero;
    priority = [0 for _ in range(N_ue)]
    tmp = []
    for i in range(N_ue):
        # Calculate q_i by equation (17);
        q_i = 0
        for j in K[i]:
            q_i = max(q_i, q[i][j])
        if q_i == 0:
            # print("err: q_i is zero!")
            continue

        # Generate primary UE set Y_i by equation (18);
        Y_i = set()
        for j in K[i]:
            Y_i = Y_i | H[j]
        Y_i = Y_i - {i}

        V_i = 0
        for k in Y_i:
            # Calculate v_ki by equation (19);
            # Calculate V_ki by equation (20);
            V_ki = 0
            for l in K[k]:
                V_ki += q[k][l] * ((r[k]-5)/(100-10))
            
            # Calculate V_i by equation (21);
            V_i += V_ki
        # end for
        
        # Calculate priority factor θ_i by equation (22);
        priority[i] = (r[i]/q_i) * (q_i - V_i)
        tmp.append([i, priority[i]])
    # end for
    # print(priority)
    # print(tmp)
    # Generate the priority order of each UE according to the order of priority factors from large to small.
    ue_order = [ue_idx for ue_idx, priority in sorted(tmp, key=lambda x: x[1], reverse=True)]
    return ue_order

def MCRAIC(N_ue:int, N_vlc:int, U:List[int], K:List[Set[int]], H:List[Set[int]], alpha:List[List[float]], required_data_rate:List[float], vlc_data_rate:List[List[List[float]]]):
    # Initialize E_i = ∅, G = ∅, A_j = ∅, D_i = ∅, Q_i = ∅, M_3×N_vlc = {0}, X_N_u×N_vlc = {0};
    E = [set() for i in range(N_ue)]
    G = []
    A = []
    D = [[] for i in range(N_ue)]
    Q = [set() for i in range(N_ue)]
    M = [[0 for _ in range(3)] for j in range(N_vlc)]
    X = [[0 for j in range(N_vlc)] for i in range(N_ue)]
    # Record the UE who connected to wifi
    wifi = []
    # The remaining band of each VLC AP
    C = [{0, 1, 2} for j in range(N_vlc)]
    # Make a copy of required data rate
    r = list(required_data_rate)
    # Sort UEs ∈ U by θi in decreasing order;
    # U is pre-sorted UE set! 
    for i in U:
        K_i = []
        for j in K[i]:
            Ui = U[i+1:]
            largest = True
            for k in (set(Ui) & H[j]):
                if alpha[i][j] <= alpha[k][j]:
                    largest = False
                    break
            # if α_ij > α_kj , ∀k ∈ (Ui ∩ H_j ) then
            if not largest:
                # remove the VLC AP-j from set K_i ;
                K_i.append(j)
            # end if
        # end for

        # Generate the candidate VLC AP list D_i = K_i ;
        for j in K_i:
            D[i].append(j)
        # if the candidate VLC AP set D_i = ∅ then
        if not D[i]:
            # UE-i is connected to the WiFi AP;
            E[i].add(7)
            wifi.append(i)
            continue
        # end if
        for j in D[i]:
            avg = 0
            for k in (set(Ui) & H[j]):
                avg += alpha[k][j]
            avg /= len(set(Ui) & H[j])
            # if α_ij < avg.(α_kj) , k ∈ (Ui ∩ H_j ) then
            if alpha[i][j] < avg:
                # add VLC AP-j into Q_i as Q_i = Q i ∪ j ;
                Q[i].add(j)
            # end if
        # end for
        # Sort APs ∈ D i by αij in increasing order;
        D_i = sorted(D[i], key=lambda j: alpha[i][j])
        for j in D_i:
            # if C_j != ∅ and UE-i is NOT satisfied then 
            if C[j] and (r[i]>0): 
                # assign an available band to UE-i;
                band = C[j].pop()
                E[i].add(band)
                # update the situation of band allocation;
                M[j][band] = i
                # Update the require data rate
                r[i] -= vlc_data_rate[band][i][j]
            # end if
            if j in Q[i]:
                # repeat the steps from 20 to 23;
                # if C_j != ∅ and UE-i is NOT satisfied then
                if C[j] and (r[i]>0): 
                    # assign an available band to UE-i;
                    band = C[j].pop()
                    E[i].add(band)
                    # update the situation of band allocation;
                    M[j][band] = i
                    # Update the require data rate
                    r[i] -= vlc_data_rate[band][i][j]
                # end if
            # end if
        # end for
        if not E[i]:
            # UE-i is connected to the WiFi AP;
            E[i].add(7)
            wifi.append(i)
            continue
        # end if
    # end for
    # print("VLC\n", M)
    # print("wifi\n", wifi)
    # print("E\n", E)
    # print("C\n", C)
    # <Todo> Sort UEs ∈ U by x_i in decreasing order;
    for i in U:
        for j in D[i]:
            # if x ij > x i and C j =∅ then
            if C[j]:
                # assign a remaining band to UE-i;
                band = C[j].pop()
                E[i].add(band)
                # update the situation of band allocation;
                M[j][band] = i
                # Update the require data rate
                r[i] -= vlc_data_rate[band][i][j]
            # end if
        # end for
    # end for
    return M, wifi, E

def MCRAIC_EXE(N_UE, FoV):

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

    # print(vlc_channel_gain)
    # p.plot_vlc_channel_gain_matrix(vlc_channel_gain)
    # print(vlc_sinr)
    # p.plot_vlc_sinr_matrix(vlc_sinr_R)
    # print(vlc_data_rate)
    # p.plot_vlc_data_rate_matrix(vlc_data_rate_R)

    



    [vlc_ap_selection_order, alpha]= VASIA(N_ue=N_UE, K=K, H=H, r=require_data_rate, distance=distance, angle=angle, optical_concentrator=optical_concentrator, FoV=FoV)
    # print(vlc_ap_selection_order)
    # print(alpha)
    ue_order = UPARU(N_ue=N_UE, K=K, H=H, r=require_data_rate, q=vlc_data_rate_R)
    # print(ue_order)
    [M, wifi, ue_allocation] = MCRAIC(N_ue=N_UE, N_vlc=cfg.N_VLC, U=ue_order, K=K, H=H, alpha=alpha, required_data_rate=require_data_rate, vlc_data_rate=vlc_data_rate)
    # p.plot_ue_allocation_2d_with_legend(ue_allocation)

    total_data_rate_of_each_ue = [0 for i in range(N_UE)]
    # Calculate total data rate obtained from VLC AP
    j = 0
    STP = 0
    for m in M:
        total_data_rate_of_each_ue[m[0]] += vlc_data_rate_R[m[0]][j]
        total_data_rate_of_each_ue[m[1]] += vlc_data_rate_G[m[1]][j]
        total_data_rate_of_each_ue[m[2]] += vlc_data_rate_B[m[2]][j]
        STP += (vlc_data_rate_R[m[0]][j] + vlc_data_rate_G[m[1]][j] + vlc_data_rate_B[m[0]][j])
        j += 1
    

    # wifi allocation #################################################################################
    wifi_channel_gain = [f.wifi_channel_gain(d=l.geometric_distance(ue_locations[i], wifi_location)) for i in range(N_UE)]
    # p.plot_wifi_channel_gain_vector(wifi_channel_gain)
    wifi_snr = [f.wifi_snr(H_wifi=wifi_channel_gain[i], N_wifi_ue=len(wifi)) for i in range(N_UE)]
    # p.plot_wifi_snr_vector(wifi_snr)
    wifi_data_rate = [f.wifi_data_rate(snr=wifi_snr[i], N_wifi_ue=len(wifi)) for i in range(N_UE)]
    #p.plot_wifi_data_rate_vector(wifi_data_rate)

    # Calculate data rate obtained from WiFi 
    for w in wifi:
        total_data_rate_of_each_ue[w] += wifi_data_rate[w]
        STP += wifi_data_rate[w]
    
    # Caculate average user satisfaction (AUS)
    AUS = 0
    for i in range(N_UE):
        if total_data_rate_of_each_ue[i]/require_data_rate[i] > 1:
            AUS += 1
        else:
            AUS += total_data_rate_of_each_ue[i]/require_data_rate[i]
    AUS /= N_UE

    # Caculate Service Fairness Index (SFI)
    SFI = 0
    upper = 0
    lower = 0
    for i in range(N_UE):
        upper += total_data_rate_of_each_ue[i]
        lower += (total_data_rate_of_each_ue[i] ** 2)
    if lower != 0:
        SFI = (upper ** 2) / (N_UE * lower)    
    else:
        SFI = 0.5

    # Calculate User Satisfaction Rate (USR)
    USR = 0
    satisfied_ue = 0
    for i in range(N_UE):
        if total_data_rate_of_each_ue[i]/require_data_rate[i] >= 1:
            satisfied_ue += 1
    USR = satisfied_ue / N_UE

    # p.plot_total_data_rate(total_data_rate_of_each_ue=total_data_rate_of_each_ue, require_data_rate=require_data_rate)
    # print("System Throughput: ", STP)
    return STP, AUS, SFI, USR