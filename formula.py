import math
import numpy as np
def dbm_to_watts(P_dbm):
        """Convert power from dBm to Watts"""
        return 10**((P_dbm - 30) / 10)  # Since 1 mW = 10^(-3) W

class Formula():

    def vlc_channel_gain(m, A_pd, d, irradiant_angle, incident_angle, Fov, optical_filter_gain, optical_concentrator):
        assert d != 0, "Distance (d) must not be zero to avoid division by zero."
        if incident_angle > Fov :
            return 0
        irradiant_angle_rad = math.radians(irradiant_angle)  # Convert degrees to radians
        incident_angle_rad = math.radians(incident_angle)
        return ((m+1)*A_pd*(math.cos(irradiant_angle_rad) ** m)*math.cos(incident_angle_rad)*optical_concentrator*optical_filter_gain)/(2*math.pi*(d ** 2))
    
    def lambertian_emission_order(semi_angle_at_helf_power):
        if semi_angle_at_helf_power <= 0 or semi_angle_at_helf_power >= 90:
            raise ValueError("Semi-angle must be in the range (0, 90) degrees.")
        semi_angle_at_helf_power_rad = math.radians(semi_angle_at_helf_power)
        return -math.log(2)/math.log(math.cos(semi_angle_at_helf_power_rad))

    def optical_concentrator(incident_angle, Fov):
        if incident_angle > Fov :
            return 0
        n = 1.5
        Fov_rad = math.radians(Fov)
        return (n**2)/(math.sin(Fov_rad)**2)

    def vlc_sinr(oe_conversion, P_vlc, H_vlc, shot, thermal, interference):
        return ((oe_conversion*P_vlc*H_vlc)**2)/((shot**2)+(thermal**2)+interference)
    
    def shot_noise(P_sig, P_ici):
        q = 1.6e-19
        Re = 0.54
        B = 10e6 
        I_bg = 5.1e-3 
        I_2 = 0.562
        return 2*q*Re*(P_sig+P_ici)*B + 2*q*I_bg*I_2*B

    def thermal_noise():
        k = 1.28e-23
        Tk = 300 # room temperature 27 degree Celsius 
        fix_capacitance_pd = 112e-12
        fet_factor = 1.5
        B = 10e6
        A = 1
        I_2 = 0.562
        I_3 = 0.0868
        G = 10
        gm = 3e-3       
        return ((8*math.pi*k*Tk)/G)*fix_capacitance_pd*A*I_2*(B**2) + ((16*(math.pi**2)*k*Tk*fet_factor)/gm)*(fix_capacitance_pd**2)*(A**2)*I_3*(B**3)

    def vlc_data_rate(B_vlc, sinr):
        return B_vlc * math.log2(1+sinr)
    
    def wifi_channel_gain(h_r, L_d):
        return (10 ** (-L_d/20)) * h_r
    
    def generate_rayleigh_hr(avg_power_dB=2.46):
        """
        Generate a Rayleigh fading gain h_r with a specified average power in dB.
        """
        P_linear = 10 ** (avg_power_dB / 10)
        sigma = np.sqrt(P_linear / 2)
        return np.random.rayleigh(scale=sigma)

    def large_scale_fading_loss(d):
        # Set parameters
        mean = 0       # Zero-mean
        std_dev = 1.8  # Standard deviation in dB
        # Generate one sample of Z
        Z = np.random.normal(loc=mean, scale=std_dev)
        return 68 + 10*1.6*math.log10(d/1) + Z  
    
    def wifi_sinr(P_wifi, H_wifi, N_wifi, B_wifi):
        return (dbm_to_watts(P_wifi)*(H_wifi ** 2))/(dbm_to_watts(N_wifi)*B_wifi)
    
    def wifi_data_rate(B_wifi, sinr):
        return B_wifi * math.log2(1+sinr)
    