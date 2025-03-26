import math
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
    
    def vlc_sinr(oe_conversion, P_vlc, H_vlc, shot, thermal, interference):
        return ((oe_conversion*P_vlc*H_vlc)**2)/((shot**2)+(thermal**2)+interference)
    
    def vlc_data_rate(B_vlc, sinr):
        return B_vlc * math.log2(1+sinr)
    
    def wifi_channel_gain(h_r, L_d):
        return (10 ** (-L_d/20)) * h_r
    
    def wifi_sinr(P_wifi, H_wifi, N_wifi, B_wifi):
        return (dbm_to_watts(P_wifi)*(H_wifi ** 2))/(dbm_to_watts(N_wifi)*B_wifi)
    
    def wifi_data_rate(B_wifi, sinr):
        return B_wifi * math.log2(1+sinr)
    