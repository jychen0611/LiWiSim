import unittest
import math
from formula import Formula
from location import Location

class Test_VLC_Channel_Gain(unittest.TestCase):
    def test_normal_case(self):
        result = Formula.vlc_channel_gain(m=1, A_pd=1e-4, d=1, irradiant_angle=60, incident_angle=60, Fov=60, optical_filter_gain=1, optical_concentrator=1)
        self.assertAlmostEqual(result, 7.95774e-6, places=7)

    def test_outside_fov(self):
        result = Formula.vlc_channel_gain(m=1, A_pd=1e-4, d=1, irradiant_angle=30, incident_angle=70, Fov=60, optical_filter_gain=1, optical_concentrator=1)
        self.assertEqual(result, 0)

    def test_zero_distance(self):
        with self.assertRaises(AssertionError) as context:
            Formula.vlc_channel_gain(m=1, A_pd=1e-4, d=0, irradiant_angle=30, incident_angle=20, Fov=60, optical_filter_gain=1, optical_concentrator=1)
        # Check the exact error message
        self.assertEqual(str(context.exception), "Distance (d) must not be zero to avoid division by zero.")

    def test_zero_aperture_area(self):
        result = Formula.vlc_channel_gain(m=1, A_pd=0, d=1, irradiant_angle=30, incident_angle=20, Fov=60, optical_filter_gain=1, optical_concentrator=1)
        self.assertEqual(result, 0)

class Test_VLC_SINR(unittest.TestCase):
    def test_normal_case(self):
        result = Formula.vlc_sinr(oe_conversion=0.44, P_vlc=20, H_vlc=8e-6, shot=0.1, thermal=0.2, interference=1)
        self.assertAlmostEqual(result, 4.72015238e-9, places=7)
   

class Test_VLC_Data_Rate(unittest.TestCase):
    def test_normal_case(self):
        result = Formula.vlc_data_rate(B_vlc=20e6, sinr=4.72015238e-9)
        self.assertAlmostEqual(result, 0.13619, places=5)


class Test_WiFi_Channel_Gain(unittest.TestCase):
    def test_normal_case(self):
        result = Formula.wifi_channel_gain(h_r=1, L_d=20)
        self.assertAlmostEqual(result, 0.1, places=1)

class Test_WiFi_SINR(unittest.TestCase):
    def test_normal_case(self):
        result = Formula.wifi_sinr(P_wifi=20, H_wifi=0.1, N_wifi=-174, B_wifi=20e6)
        self.assertAlmostEqual(result, 12559432157.547861, places=6)


class Test_WiFi_Data_Rate(unittest.TestCase):
    def test_normal_case(self):
        result = Formula.wifi_data_rate(B_wifi=20e6, sinr=12559432157.547861)
        self.assertAlmostEqual(result, 670961043.7388686, places=7)

# Room size
L = 10 # m
W = 10 # m
H = 3 # m  
class TestLocationFunctions(unittest.TestCase):
    def test_generate_ue_location_within_bounds(self):
        for _ in range(100):
            x, y, z = Location.generate_ue_location()
            self.assertGreaterEqual(x, 0)
            self.assertLessEqual(x, L)
            self.assertGreaterEqual(y, 0)
            self.assertLessEqual(y, W)
            self.assertEqual(z, 0)

    def test_generate_vlc_location_count_and_values(self):
        vlc_locs = Location.generate_vlc_location()
        self.assertEqual(len(vlc_locs), 16)
        for x, y, z in vlc_locs:
            self.assertIn(x, [2, 4, 6, 8])
            self.assertIn(y, [2, 4, 6, 8])
            self.assertEqual(z, H)

    def test_geometric_distance_known_values(self):
        self.assertAlmostEqual(Location.geometric_distance((0, 0, 0), (3, 4, 0)), 5.0)
        self.assertAlmostEqual(Location.geometric_distance((0, 0, 0), (0, 0, 5)), 5.0)
        self.assertAlmostEqual(Location.geometric_distance((1, 2, 3), (4, 6, 3)), 5.0)
        self.assertAlmostEqual(Location.geometric_distance((0, 0, 0), (0, 0, 0)), 0.0)



if __name__ == "__main__":
    unittest.main()