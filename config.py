def dbm_to_watts(P_dbm):
    """Convert power from dBm to Watts"""
    return 10**((P_dbm - 30) / 10)  # Since 1 mW = 10^(-3) W

# Room size
L = 10 # m
W = 10 # m
H = 3 # m
# Height of receiving plane
H_PD = 1.2 # m
# Transmit optical power per LED
P_TX_VLC_R = dbm_to_watts(20) * 0.333 # W
P_TX_VLC_G = dbm_to_watts(20) * 0.38 # W
P_TX_VLC_B = dbm_to_watts(20) * 0.287 # W
# VLC system bandwidth
B_VLC = 20 # Hz
# Semi-angle at half power
SEMI_ANGLE_AT_HELF_POWER = 60 # degree 
# Optical filter gain
OPTICAL_FILTER_GAIN = 1 
# Physical area of the PD
A_PD = 1 # cm^2
# O/E conversion coefficient
R_OE = 0.44 # A/W
G_OE = 0.23 # A/W
B_OE = 0.15 # A/W
# Wifi transmit power
P_TX_WIFI = 20 # dBm 
# Wifi bandwidth
B_WIFI = 20 # MHz
# Wifi noise spectral density
WIFI_NOISE = -174 # dBm/Hz
# Wifi receiver power range
P_WIFI_MIN = -125 # dBm
P_WIFI_MAX = 50 # dBm
# PD light power range
P_VLC_MIN = 50e-6 # W
P_VLC_MAX = 10e-3 # W

# Number of VLC APs
N_VLC = 16
# Number of WiFi APs
N_WIFI = 1
# Default number of UEs
N_UE = 25
# Default field of view angle of PD
F_O_V = 60 # degree

# Experiment times
TIMES = 10