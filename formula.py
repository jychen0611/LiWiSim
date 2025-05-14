import config as cfg
import math
import numpy as np
import random

def dbm_to_watts(P_dbm):
    """Convert power from dBm to Watts"""
    return 10**((P_dbm - 30) / 10)  # Since 1 mW = 10^(-3) W

def generate_log_normal_shadowing(std_dev_db=10):
    """
    Generate log-normal shadowing in dB.
    Xσ ~ N(0, std_dev_db^2)
    """
    return np.random.normal(loc=0.0, scale=std_dev_db)

def wifi_channel_to_frequency(channel, band='2.4GHz'):
    """
    Convert Wi-Fi channel number to carrier frequency (MHz).
    
    Parameters:
        channel (int): Wi-Fi channel number
        band (str): '2.4GHz', '5GHz', or '6GHz'
        
    Returns:
        frequency in MHz or None if invalid
    """
    if band == '2.4GHz':
        if 1 <= channel <= 13:
            return 2412 + (channel - 1) * 5
        elif channel == 14:
            return 2484
    elif band == '5GHz':
        if 36 <= channel <= 64:
            return 5000 + channel * 5
        elif 100 <= channel <= 144:
            return 5000 + channel * 5
        elif 149 <= channel <= 165:
            return 5000 + channel * 5
    elif band == '6GHz':
        if 1 <= channel <= 233:
            return 5955 + (channel - 1) * 5
    return None

def generate_rayleigh_hr(avg_power_dB=2.46):
    """
    Generate a Rayleigh fading gain h_r with a specified average power in dB.
    """
    P_linear = 10 ** (avg_power_dB / 10)
    sigma = np.sqrt(P_linear / 2)
    return np.random.rayleigh(scale=sigma)

def large_scale_fading_loss(d):
    f = wifi_channel_to_frequency(channel=random.randint(1, 14)) * 1e6
    return 20 * math.log10(d*f) - 147.55 

def get_ru_bandwidth_mhz(N_wifi_ue):
    # Valid RU mappings for 20 MHz
    ru_table = {
        1: 20,        # full 20 MHz = 1 × 242-tone RU
        2: 10,        # 2 × 106-tone RUs (~10 MHz each)
        3: 5,
        4: 5,         # 4 × 52-tone RUs (~5 MHz each)
        5: 2.5, 
        6: 2.5,
        7: 2.5,
        8: 2.5,       # 8 × 26-tone RUs (~2.5 MHz each)
        9: 2.22       # 9 × 26-tone RUs (~2.22 MHz each)
    }

    if N_wifi_ue in ru_table:
        return ru_table[N_wifi_ue]
    else:
        return 2.22
        # raise ValueError(f"802.11ax 20 MHz channel does not support {N_wifi_ue} UEs with valid RU sizes.")

class Formula():

    def vlc_channel_gain(d:float, irradiant_angle:float, incident_angle:float, optical_concentrator:float):
        m = 1.0000000000000002
        A_pd = cfg.A_PD
        Fov = cfg.F_O_V
        optical_filter_gain = cfg.OPTICAL_FILTER_GAIN

        assert d != 0, "Distance (d) must not be zero to avoid division by zero."
        if incident_angle > Fov :
            return 0
        irradiant_angle_rad = math.radians(irradiant_angle)  # Convert degrees to radians
        incident_angle_rad = math.radians(incident_angle)
        return ((m+1)*A_pd*(math.cos(irradiant_angle_rad) ** m)*math.cos(incident_angle_rad)*optical_concentrator*optical_filter_gain)/(2*math.pi*(d ** 2))
    
    def lambertian_emission_order():
        semi_angle_at_helf_power = cfg.SEMI_ANGLE_AT_HELF_POWER
        if semi_angle_at_helf_power <= 0 or semi_angle_at_helf_power >= 90:
            raise ValueError("Semi-angle must be in the range (0, 90) degrees.")
        semi_angle_at_helf_power_rad = math.radians(semi_angle_at_helf_power)
        return -math.log(2)/math.log(math.cos(semi_angle_at_helf_power_rad))

    def optical_concentrator(incident_angle:float):
        Fov=cfg.F_O_V
        if incident_angle > Fov :
            return 0
        n = 1.5
        Fov_rad = math.radians(Fov)
        return (n**2)/(math.sin(Fov_rad)**2)

    def vlc_sinr(H_vlc:float, shot:float, interference:float, band:int):
        if band == 0:
            P_tx_vlc = cfg.P_TX_VLC_R # dBm
        elif band == 1:
            P_tx_vlc = cfg.P_TX_VLC_G # dBm
        elif band == 2:
            P_tx_vlc = cfg.P_TX_VLC_B # dBm
        oe_conversion = cfg.R_OE
        thermal = 3.301237784295836e-10
        # PD light power range
        P_v_min = cfg.P_VLC_MIN # W
        P_v_max = cfg.P_VLC_MAX # W

        P_rx_watts = P_tx_vlc * H_vlc 
        P_rx_watts_clamped = np.clip(P_rx_watts, P_v_min, P_v_max) 
        return ((oe_conversion*P_rx_watts_clamped)**2)/(shot+thermal+interference)
    
    def shot_noise(P_sig:float, P_ici:float):
        q = 1.6e-19
        Re = 0.54
        B = 10 
        I_bg = 5.1e-3 
        I_2 = 0.562
        return 2*q*Re*(P_sig+P_ici)*B + 2*q*I_bg*I_2*B

    def thermal_noise():
        k = 1.28e-23
        Tk = 300 # room temperature 27 degree Celsius 
        fix_capacitance_pd = 112
        fet_factor = 1.5
        B = 10
        A = 1
        I_2 = 0.562
        I_3 = 0.0868
        G = 10
        gm = 3e-3       
        return ((8*math.pi*k*Tk)/G)*fix_capacitance_pd*A*I_2*(B**2) + ((16*(math.pi**2)*k*Tk*fet_factor)/gm)*(fix_capacitance_pd**2)*(A**2)*I_3*(B**3)

    def vlc_data_rate(sinr:float):
        B_vlc = cfg.B_VLC / 3 # R / G / B band
        return B_vlc * math.log2(1+sinr)
    
    def wifi_channel_gain(d:float):
        h_r = generate_rayleigh_hr()
        L_d = large_scale_fading_loss(d=d)
        return (h_r**2) * (10 ** ((-L_d+generate_log_normal_shadowing()) / 10))  # Rayleigh power * path loss
    
    def wifi_snr(H_wifi:float, N_wifi_ue:int):
        P_tx_wifi = cfg.P_TX_WIFI # dbm
        N_wifi = cfg.WIFI_NOISE # dBm
        B_wifi = cfg.B_WIFI * 1e6 # Hz
        P_rx_min = cfg.P_WIFI_MIN # dBm
        P_rx_max = cfg.P_WIFI_MAX # dBm

        P_rx_watts = (dbm_to_watts(P_tx_wifi) / N_wifi_ue) * H_wifi
        P_rx_dbm = 10 * np.log10(P_rx_watts) + 30
        P_rx_dbm = np.clip(P_rx_dbm, P_rx_min, P_rx_max)
        P_rx_watts_clamped = dbm_to_watts(P_rx_dbm)
        return P_rx_watts_clamped / (dbm_to_watts(N_wifi)*B_wifi)
    
    def wifi_data_rate(snr:float, N_wifi_ue:int):
        B_wifi = get_ru_bandwidth_mhz(N_wifi_ue=N_wifi_ue)
        return B_wifi * math.log2(1+snr)
    