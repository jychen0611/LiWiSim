def VASIA():
    # for i in range(N_ue):
        # for j in K[i]:
            # Calculate q_ij by equation (9)
            # Generate the primary UE set Y_ij 
          
            # for k in Y_ij:
                # Calculate v_k_ij by equation (10)
                # Calculate V_k_ij by equation (11)
            # end for
        # end for
        
        # Generate Z_ij by equation (12)
        
        # for l in Z_ij:
            # Calculate v_l_ij by equation (13) 
            # Calculate V_l_ij by equation (14)
        # end for

        # Calculate V_ij by equation (15)
        # Calculate alpha_ij by equation (16)
    # end for
    
    # Generate the VLC AP selection order of UE_i by the order of alpha_ij from small to large.
    return 

def UPARU():
    # Initialize the priority factor of each UE to zero;
    
    # for i in (N_ue):
        # Calculate q_i by equation (17);
        # Generate Y_i by equation (18);
      
        # for k in Y_i:
            # Calculate v_ki by equation (19);
            # Calculate V_ki by equation (20);
        # end for
        
        # Calculate V_i by equation (21);
        # Calculate θ_i by equation (22);
    
    # end for
    
    # Generate the priority order of each UE according to the order of priority factors from large to small.
    return

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