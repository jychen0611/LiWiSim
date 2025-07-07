'''
Each UE is an agent.

Input state to each agent is the requrie data rate / distance to nearest VLC AP / N_UE in that VLC AP coverage.

Action is a 1-bit vector (0: WiFi, 1:LiFi )

The reward encourages to maximize the system throughput.
'''

import config as cfg
from location import Location as l
from formula import Formula as f
from plot import Plot as p

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque

# Constants
N_VLC = cfg.N_VLC
STATE_DIM = 3  # [required_rate, distance_to_nearest_VLC, N_UE_in_nearest_VLC_coverage]
ACTION_DIM = 2  # 0: WiFi, 1: LiFi

# Automatically choose the computing device:
# Use GPU (CUDA) if available; otherwise, fall back to CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# DQN Network (shared)
class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, output_dim)
        )

    def forward(self, x):
        return self.net(x)

# Replay Buffer
class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state):
        self.buffer.append((state, action, reward, next_state))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        state, action, reward, next_state = map(np.array, zip(*batch))
        return state, action, reward, next_state

    def __len__(self):
        return len(self.buffer)

# Environment
class HybridNetworkEnv:
    def __init__(self, N_UE):
        self.n_ue = N_UE

    def initialize_hybrid_network(self):
        # Uniformly generate the location of each VLC AP/UE
        ue_locations = [l.generate_ue_location() for _ in range(self.n_ue)]
        vlc_locations = l.generate_vlc_location(cfg.N_VLC)
        # Define location of WiFi AP
        wifi_location = (cfg.L/2, cfg.W/2, cfg.H)

        # Visualize LiWi Network 
        # p.plot_network_distribution(ue_locations, vlc_locations, wifi_location)
        # p.plot_network_distribution_with_labels(ue_locations, vlc_locations, wifi_location)

        # Generate the required data rate (Mbps) of each UE
        rate_options = {10, 20, 40, 60, 80, 100}
        require_data_rate = [random.choice(list(rate_options)) for i in range(self.n_ue)]

        return ue_locations, vlc_locations, wifi_location, require_data_rate
    
    def set_state(self, distance, remain_data_rate, K, H):
        state = []
        ap_idx_list = []
        for i in range(self.n_ue):
            d = 100
            ap_idx = -1
            for j in K[i]:
                if distance[i][j] < d:
                    d = distance[i][j]
                    ap_idx = j
            ap_idx_list.append(ap_idx)
            s_i = [remain_data_rate[i], d, len(H[ap_idx])] 
            state.append(s_i)
        return state, ap_idx_list
    
    def calculate_vlc_data_rate(self, distance, angle, optical_concentrator, FoV, K):
        # Calculate VLC data rate based on R-band / G-band / B-band
        vlc_channel_gain = [[0 for j in range(cfg.N_VLC)] for i in range(self.n_ue)]
        vlc_sinr_R = [[0 for j in range(cfg.N_VLC)] for i in range(self.n_ue)]
        vlc_data_rate_R = [[0 for j in range(cfg.N_VLC)] for i in range(self.n_ue)]
        vlc_sinr_G = [[0 for j in range(cfg.N_VLC)] for i in range(self.n_ue)]
        vlc_data_rate_G = [[0 for j in range(cfg.N_VLC)] for i in range(self.n_ue)]
        vlc_sinr_B = [[0 for j in range(cfg.N_VLC)] for i in range(self.n_ue)]
        vlc_data_rate_B = [[0 for j in range(cfg.N_VLC)] for i in range(self.n_ue)]
        # For each UE
        for i in range(self.n_ue):
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
        return vlc_data_rate
    
    def calculate_wifi_data_rate(self, N_wifi_UE, ue_locations, wifi_location):
        # Caculate the WiFi data rate of each UE
        wifi_channel_gain = [f.wifi_channel_gain(d=l.geometric_distance(ue_locations[i], wifi_location)) for i in range(self.n_ue)]
        # p.plot_wifi_channel_gain_vector(wifi_channel_gain)
        wifi_snr = [f.wifi_snr(H_wifi=wifi_channel_gain[i], N_wifi_ue=N_wifi_UE) for i in range(self.n_ue)]
        # p.plot_wifi_snr_vector(wifi_snr)
        wifi_data_rate = [f.wifi_data_rate(snr=wifi_snr[i], N_wifi_ue=N_wifi_UE) for i in range(self.n_ue)]
        #p.plot_wifi_data_rate_vector(wifi_data_rate)
        return wifi_data_rate
    
    def resource_allocator(self, actions, state, vlc_data_rate, ap_idx_list, wifi_data_rate, K, H, require_data_rate):
        # record reward 
        reward = 0
        wifi = []
        lifi = []
        for i in range(self.n_ue):
            if actions[i] == 1:
                lifi.append(i)
            else:
                wifi.append(i)

        STP = 0
        total_data_rate_of_each_ue = [0 for i in range(self.n_ue)]

        # Generate UE priority with (1/vlc_data_rate[0][i][ap_idx_list[i]])
        ue_priority = []
        for i in range(self.n_ue):
            if vlc_data_rate[0][i][ap_idx_list[i]] != 0:
                priority = 1/vlc_data_rate[0][i][ap_idx_list[i]]
                ue_priority.append(priority)
            else:
                ue_priority.append(np.finfo(np.float32).max)
        # Sort VLC UE with UE priority
        lifi_sorted = sorted(lifi, key=lambda ue: ue_priority[ue])

        # The remaining band of each VLC AP
        C = [{0, 1, 2} for j in range(N_VLC)]
        # lifi allocation #################################################################################
        for ue in lifi_sorted:
            best = ap_idx_list[ue]
            if best == -1:
                continue
            while C[best]:
                # assign an available band to UE-i;
                band = C[best].pop()
                total_data_rate_of_each_ue[ue] += vlc_data_rate[band][ue][best]
                # Update STP
                STP += vlc_data_rate[band][ue][best]
                # Update reward
                reward += vlc_data_rate[band][ue][best]
                # Update the require data rate
                state[ue][0] -= vlc_data_rate[band][ue][best]

                if state[ue][0] <= 0:
                    break

        # Generate UE priority with len(K[i])
        ue_priority = []
        for i in range(self.n_ue):
            priority = len(K[i])
            ue_priority.append(priority)
          
        # Sort VLC UE with UE priority
        lifi_sorted = sorted(lifi, key=lambda ue: ue_priority[ue])

        # (skip reward)            
        for ue in lifi_sorted:
            if total_data_rate_of_each_ue[ue] == 0:
                for ap in K[ue]:
                    if C[ap]:
                        # assign an available band to UE-i;
                        band = C[ap].pop()
                        total_data_rate_of_each_ue[ue] += vlc_data_rate[band][ue][ap]
                        # Update STP
                        STP += vlc_data_rate[band][ue][ap]
                        # Update reward
                        reward += vlc_data_rate[band][ue][ap]
                        # Update the require data rate
                        state[ue][0] -= vlc_data_rate[band][ue][ap]

                        if state[ue][0] <= 0:
                            break
        
        # (skip reward)                      
        for ue in lifi_sorted:
            if state[ue][0] > 0:
                for ap in K[ue]:
                    while C[ap]:
                        # assign an available band to UE-i;
                        band = C[ap].pop()
                        total_data_rate_of_each_ue[ue] += vlc_data_rate[band][ue][ap]
                        # Update STP
                        STP += vlc_data_rate[band][ue][ap]
                        # Update reward
                        reward += vlc_data_rate[band][ue][ap]
                        # Update the require data rate
                        state[ue][0] -= vlc_data_rate[band][ue][ap]
                        
                        if state[ue][0] <= 0:
                            break
                    
                    if state[ue][0] <= 0:
                            break    

        for ue in lifi_sorted:
            best = ap_idx_list[ue]
            if best == -1:
                continue
            while C[best]:
                # assign an available band to UE-i;
                band = C[best].pop()
                total_data_rate_of_each_ue[ue] += vlc_data_rate[band][ue][best]
                # Update STP
                STP += vlc_data_rate[band][ue][best]
                # Update reward
                reward += vlc_data_rate[band][ue][best]
                # Update the require data rate
                state[ue][0] -= vlc_data_rate[band][ue][best]
        
        # Generate UE priority with (state[i][0])
        ue_priority = []
        for i in range(self.n_ue):
            priority = state[i][0]
            ue_priority.append(priority)
            
        # Sort VLC UE with UE priority
        lifi_sorted = sorted(lifi, key=lambda ue: ue_priority[ue])

        # Allocate the remaining bandwidth (skip reward)
        for ue in lifi_sorted:
            for ap in K[ue]:
                while C[ap]:
                    # assign an available band to UE-i;
                    band = C[ap].pop()
                    total_data_rate_of_each_ue[ue] += vlc_data_rate[band][ue][ap]
                    # Update STP
                    STP += vlc_data_rate[band][ue][ap]
                    # Update reward
                    # reward += vlc_data_rate[band][ue][ap]
                    # Update the require data rate
                    # state[ue][0] -= vlc_data_rate[band][ue][ap]
                    

        # wifi allocation #################################################################################
        total_wifi_data_rate = 0  
        # Calculate data rate obtained from WiFi 
        for ue in wifi:
            total_data_rate_of_each_ue[ue] += wifi_data_rate[ue]
            STP += wifi_data_rate[ue]
            # Update reward
            reward += wifi_data_rate[ue] 
            # state[ue][0] -= wifi_data_rate[ue]
            total_wifi_data_rate += wifi_data_rate[ue]
        
        # Update state
        next_state = state
        
        # Caculate average user satisfaction (AUS)
        AUS = 0
        for i in range(self.n_ue):
            if total_data_rate_of_each_ue[i]/require_data_rate[i] > 1:
                AUS += 1
            else:
                AUS += total_data_rate_of_each_ue[i]/require_data_rate[i]
        AUS /= self.n_ue

        # Caculate Service Fairness Index (SFI)
        SFI = 0
        upper = 0
        lower = 0
        for i in range(self.n_ue):
            upper += total_data_rate_of_each_ue[i]
            lower += (total_data_rate_of_each_ue[i] ** 2)
        if lower != 0:
            SFI = (upper ** 2) / (self.n_ue * lower)    
        else:
            SFI = 0.5

        # Calculate User Satisfaction Rate (USR)
        USR = 0
        satisfied_ue = 0
        for i in range(self.n_ue):
            if total_data_rate_of_each_ue[i]/require_data_rate[i] >= 1:
                satisfied_ue += 1
        USR = satisfied_ue / self.n_ue

        # Calculate Outage Ratio (OTR)
        OTR = 0
        outage_ue = 0
        for i in range(self.n_ue):
            if total_data_rate_of_each_ue[i] == 0:
                outage_ue += 1
        OTR = outage_ue / self.n_ue

        return next_state, reward, STP, AUS, SFI, USR, OTR

# MARL Agent
class MultiUEAgent:
    def __init__(self, N_UE):
        self.n_ue = N_UE
        self.policy_net = DQN(STATE_DIM, ACTION_DIM).to(device)
        self.target_net = DQN(STATE_DIM, ACTION_DIM).to(device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.optim = optim.Adam(self.policy_net.parameters(), lr=1e-3)
        self.buffers = [ReplayBuffer(10000) for _ in range(self.n_ue)] # ReplayBuffer(10000)
        self.criteria = nn.MSELoss()
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_decay = 0.995 # 0.995
        self.epsilon_min = 0.1
        self.learn_step_counter = 0
        self.target_update_freq = 800

    def select_actions(self, states):
        actions = []
        for i in range(self.n_ue):
            state_tensor = torch.FloatTensor(states[i]).unsqueeze(0).to(device)
            q_values = self.policy_net(state_tensor)
            if np.random.rand() < self.epsilon:
                action = np.random.randint(0, ACTION_DIM)
            else:
                action = torch.argmax(q_values).item()
            actions.append(action)
        return np.array(actions)

    def learn(self, batch_size=64):
        for i in range(self.n_ue):
            buffer = self.buffers[i]
            if len(buffer) < batch_size:
                continue
            state, action, reward, next_state = buffer.sample(batch_size)
            state = torch.FloatTensor(state).to(device)
            next_state = torch.FloatTensor(next_state).to(device)
            action = torch.LongTensor(action).to(device)
            reward = torch.FloatTensor(reward).to(device)

            q = self.policy_net(state).gather(1, action.unsqueeze(1)).squeeze(1)
            q_next = self.target_net(next_state).max(1)[0].detach()
            target = reward + self.gamma * q_next
            loss = self.criteria(q, target)

            self.optim.zero_grad()
            loss.backward()
            self.optim.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        # Update the target network
        #self.learn_step_counter += 1
        #if self.learn_step_counter % self.target_update_freq == 0:
        #    self.target_net.load_state_dict(self.policy_net.state_dict())

def MARL_EXE(N_UE, FoV):
    # Construct environment and agents
    env = HybridNetworkEnv(N_UE)
    agent = MultiUEAgent(N_UE)
 
    # Initialize Network Environment 
    [ue_locations, vlc_locations, wifi_location, require_data_rate] = env.initialize_hybrid_network()
    
    # Lists to record information in training routine
    N_wifi_UE_list = []
    reward_list = []
    STP_list = []
    AUS_list = []
    SFI_list = []
    USR_list = []
    OTR_list = []

    # Training Loop
    for episode in range(cfg.EPISODE):
        # Update UEs location
        ue_locations = l.move_ue_positions(ue_locations)
        # Calculate the geometric distance of each AP/UE pair
        distance = [[l.geometric_distance(ue_locations[i], vlc_locations[j]) for j in range(cfg.N_VLC)] for i in range(N_UE)]
        # Calculate the geometric distance from wifi to each UE
        wifi_distance = [l.geometric_distance(ue_locations[i], wifi_location) for i in range(N_UE)]
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

        # Set remain data rate requirement
        remain_data_rate = require_data_rate.copy()

        # Get network environment state
        [state, ap_idx_list] = env.set_state(distance, remain_data_rate, K, H) 

        # Each UE, acting as an agent, selects an action
        actions = agent.select_actions(state)

        # Calculate VLC data rate based on R-band / G-band / B-band
        vlc_data_rate = env.calculate_vlc_data_rate(distance, angle, optical_concentrator, FoV, K)

        # Check the number of UE that connected to WiFi
        N_wifi_UE = 0
        for i in actions:
            if i == 0:
                N_wifi_UE += 1
        
        # Adjust the threshold by current FoV
        if FoV <= 35:
            threshold = N_UE/2
        elif FoV <= 45:
            threshold = N_UE/3
        else:
            threshold = 5 
        
        if threshold < 5:
            threshold = 5
            
        # If the number of UE connected to wifi smaller than threshold, let outage UE use wifi
        if N_wifi_UE < threshold:
            ue_idx = [i for i in range(N_UE)]
            # Generate UE priority with wifi_diatance
            ue_priority = []
            for i in range(N_UE):
                priority = wifi_distance[i]
                ue_priority.append(priority)
            
            # Sort VLC UE with UE priority
            ue_sorted = sorted(ue_idx, key=lambda ue: ue_priority[ue])

            for i in ue_sorted:
                if len(K[i]) == 0:
                    actions[i] = 0
                    N_wifi_UE += 1
                
                if N_wifi_UE >= threshold:
                    break
        
        # If no UEs choose WiFi, force the UE closest to the WiFi AP to associate with it
        #if N_wifi_UE == 0 and FoV >= :
        #    wifi_ue = np.argmin(wifi_distance)
        #    actions[wifi_ue] = 0
        #    N_wifi_UE += 1
        
        # Calculate wifi data rate
        wifi_data_rate = env.calculate_wifi_data_rate(N_wifi_UE, ue_locations, wifi_location)

        # Resource allocation
        next_state, reward, STP, AUS, SFI, USR, OTR = env.resource_allocator(actions, state, vlc_data_rate, ap_idx_list, wifi_data_rate, K, H, require_data_rate)
        
        # Push experiences into replay buffer
        for i in range(N_UE):
            for j in range((int)(25/N_UE)):
                agent.buffers[i].push(state[i], actions[i], reward, next_state[i])
        agent.learn()
        
        if episode % 100 == 0:
            print(f"Episode {episode}, epsilon: {agent.epsilon:.2f}, reward: {reward:.2f}, action: {actions}")
        
        N_wifi_UE_list.append(N_wifi_UE)
        reward_list.append(reward)
        STP_list.append(STP)
        AUS_list.append(AUS)
        SFI_list.append(SFI)
        USR_list.append(USR)
        OTR_list.append(OTR)

    # Plot episode related diagrams
    if cfg.PLOT_EPISODE_RELATED_DIAGRAM:
        p.plot_episode_vs_N_wifi_UE(N_wifi_UE_list, len(N_wifi_UE_list))
        p.plot_episode_vs_reward(reward_list) 
        p.plot_episode_vs_STP(STP_list)  
        p.plot_episode_vs_AUS(AUS_list)  
        p.plot_episode_vs_SFI(SFI_list)  
        p.plot_episode_vs_USR(USR_list)

    # Use the average of the last 100 entries as the final result
    STP_last_100 = STP_list[-100:]
    AUS_last_100 = AUS_list[-100:]
    SFI_last_100 = SFI_list[-100:]
    USR_last_100 = USR_list[-100:]
    OTR_last_100 = OTR_list[-100:]
    STP = sum(STP_last_100) / 100
    AUS = sum(AUS_last_100) / 100
    SFI = sum(SFI_last_100) / 100
    USR = sum(USR_last_100) / 100
    OTR = sum(OTR_last_100) / 100
    return STP, AUS, SFI, USR, OTR

