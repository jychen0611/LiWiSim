from typing import List, Set
from formula import Formula as f
from location import Location as l
from plot import Plot as p

class Algorithm():
    def VASIA(N_ue:int, K:List[Set[int]], H:List[Set[int]], r:List[int], distance:List[List[float]], angle:List[List[float]], optical_concentrator:List[List[float]]) -> List[List[int]]:

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
                H_vlc = f.vlc_channel_gain(d = distance[i][j], irradiant_angle=angle[i][j], incident_angle=angle[i][j], optical_concentrator=optical_concentrator[i][j])
                interference = 0
                P_ici = 0
                for k in K[i]:
                    if k==j:
                        continue 
                    P_ici += 0.44*6.66*f.vlc_channel_gain(d = distance[i][k], irradiant_angle=angle[i][k], incident_angle=angle[i][k], optical_concentrator=optical_concentrator[i][k])
                    interference += (0.44*6.66*f.vlc_channel_gain(d = distance[i][k], irradiant_angle=angle[i][k], incident_angle=angle[i][k], optical_concentrator=optical_concentrator[i][k])) ** 2 
                shot = f.shot_noise(P_sig=0.44*6.66*H_vlc, P_ici=P_ici)
                sinr = f.vlc_sinr(H_vlc=H_vlc, shot=shot, interference=interference)
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
        return vlc_ap_selection_order

    def UPARU(N_ue:int, K:List[Set[int]], H:List[Set[int]], r:List[int], q:List[List[float]]):
        # Initialize the priority factor of each UE to zero;
        priority = [0 for _ in range(N_ue)]
        tmp = []
        for i in range(N_ue):
            # Calculate q_i by equation (17);
            q_i = 0
            for j in K[i]:
                q_i = max(q_i, q[i][j])
            
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

    def MCRAIC():
        # Initialize E i = ∅, G = ∅, Aj = ∅, D i = ∅, Q i = ∅, M 3×Nvlc = {0}, X Nu ×Nvlc = {0};
        # Sort UEs ∈ U by θi in decreasing order;
        # for each UE − i ∈ U do
            # for each VLC AP − j ∈ K i do
                # if αij > α i′j , ∀i ′ ∈ (U i ∩ H j ) then
                    # remove the VLC AP-j from set K i ;
                # end if
            # end for
            # Generate the candidate VLC AP set D i = K i ;
            # if the candidate VLC AP set D i = ∅ then
                # UE-i is connected to the WiFi AP;
            # end if
            # for each VLC AP − j ∈ D i do
                # if αij < αi ′j , i ′ ∈ (U i ∩ H j ) then
                    # add VLC AP-j into Q i as Q i = Q i ∪ j ;
                # end if
            # end for
            # Sort APs ∈ D i by αij in increasing order;
            # for each VLC AP − j ∈ D i do
                # if C j =∅ and UE-i is NOT satisfied then
                    # assign an available band to UE-i;
                    # update the situation of band allocation;
                # end if
                # if VLC AP−j ∈ Q i then
                    # repeat the steps from 20 to 23;
                # end if
            # end for
            # if E i is empty then
                # UE-i is connected to the WiFi AP;
            # end if
        # end for
        # Sort UEs ∈ U by xi in decreasing order;
        # for each UE − i ∈ U do
            # for each VLC AP−j ∈ Q i do
                # if x ij > x i and C j =∅ then
                    # assign a remaining band to UE-i;
                    # update the situation of band allocation;
                # end if
            # end for
        # end for
        return