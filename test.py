import unittest
import math
import numpy as np
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


class TestLambertianEmissionOrder(unittest.TestCase):

    def test_zero_degree(self):
        result = Formula.lambertian_emission_order(0)
        self.assertAlmostEqual(result, 0.0, places=6)

    def test_known_value_60_degree(self):
        # At 60°, cos(60°) = 0.5, so log(0.5) = -ln(2), so the result should be 1
        result = Formula.lambertian_emission_order(60)
        self.assertAlmostEqual(result, 1.0, places=6)

    def test_known_value_45_degree(self):
        # Approximate expected result for 45°
        expected = -math.log(2) / math.log(math.cos(math.radians(45)))
        result = Formula.lambertian_emission_order(45)
        self.assertAlmostEqual(result, expected, places=6)

    def test_invalid_value_over_90(self):
        with self.assertRaises(ValueError):
            Formula.lambertian_emission_order(91)

    def test_negative_angle(self):
        with self.assertRaises(ValueError):
            Formula.lambertian_emission_order(-10)

class TestOpticalConcentrator(unittest.TestCase):

    def test_within_fov(self):
        """Test output when incident angle is less than FOV"""
        result = Formula.optical_concentrator(20, 60)
        expected = (1.5**2) / (math.sin(math.radians(60))**2)
        self.assertAlmostEqual(result, expected, places=6)

    def test_equal_to_fov(self):
        """Test output when incident angle equals FOV"""
        result = Formula.optical_concentrator(60, 60)
        expected = (1.5**2) / (math.sin(math.radians(60))**2)
        self.assertAlmostEqual(result, expected, places=6)

    def test_exceeding_fov(self):
        """Test output when incident angle is greater than FOV"""
        result = Formula.optical_concentrator(70, 60)
        self.assertEqual(result, 0)

    def test_output_type(self):
        """Ensure the output is a float when angle is within FOV"""
        result = Formula.optical_concentrator(30, 60)
        self.assertIsInstance(result, float)

    def test_zero_fov(self):
        """Test behavior when FOV is zero"""
        with self.assertRaises(ZeroDivisionError):
            Formula.optical_concentrator(0, 0)

class Test_VLC_SINR(unittest.TestCase):
    def test_normal_case(self):
        result = Formula.vlc_sinr(oe_conversion=0.44, P_vlc=20, H_vlc=8e-6, shot=0.1, thermal=0.2, interference=1)
        self.assertAlmostEqual(result, 4.72015238e-9, places=7)
   
class TestShotNoise(unittest.TestCase):

    def test_known_values(self):
        """Test output with known input values"""
        result = Formula.shot_noise(1e-3, 2e-3)
        # Calculate expected value manually
        q = 1.6e-19
        Re = 0.54
        B = 10e6
        I_bg = 5.1e-3
        I_2 = 0.562
        expected = 2*q*Re*(1e-3 + 2e-3)*B + 2*q*I_bg*I_2*B
        self.assertAlmostEqual(result, expected, places=30)

    def test_zero_input(self):
        """Test output when both signal and ICI powers are zero"""
        result = Formula.shot_noise(0, 0)
        q = 1.6e-19
        B = 10e6
        I_bg = 5.1e-3
        I_2 = 0.562
        expected = 2*q*I_bg*I_2*B
        self.assertAlmostEqual(result, expected, places=30)

    def test_output_type(self):
        """Ensure output is a float"""
        result = Formula.shot_noise(0.001, 0.002)
        self.assertIsInstance(result, float)

    def test_large_input(self):
        """Test behavior with large input values"""
        result = Formula.shot_noise(1, 1)
        self.assertGreater(result, 0)

    def test_small_input(self):
        """Test behavior with very small input values"""
        result = Formula.shot_noise(1e-12, 1e-12)
        self.assertGreater(result, 0)

class TestThermalNoise(unittest.TestCase):

    def test_output_type(self):
        """Ensure the output is a float"""
        result = Formula.thermal_noise()
        self.assertIsInstance(result, float)

    def test_output_positive(self):
        """Thermal noise power should be a positive value"""
        result = Formula.thermal_noise()
        self.assertGreater(result, 0)

    def test_repeatability(self):
        """Ensure the function returns the same value each time"""
        val1 = Formula.thermal_noise()
        val2 = Formula.thermal_noise()
        self.assertAlmostEqual(val1, val2, places=30)

    def test_manual_expected_value(self):
        """Manually compute expected thermal noise value and compare"""
        k = 1.28e-23
        Tk = 300
        fix_cap = 112
        fet_factor = 1.5
        B = 10e6
        A = 1
        I_2 = 0.562
        I_3 = 0.0868
        G = 10
        gm = 3e-3

        expected = ((8 * math.pi * k * Tk) / G) * fix_cap * A * I_2 * (B ** 2) + \
                   ((16 * (math.pi ** 2) * k * Tk * fet_factor) / gm) * (fix_cap ** 2) * (A ** 2) * I_3 * (B ** 3)
        actual = Formula.thermal_noise()
        self.assertAlmostEqual(actual, expected, places=30)

class Test_VLC_Data_Rate(unittest.TestCase):
    def test_normal_case(self):
        result = Formula.vlc_data_rate(B_vlc=20e6, sinr=4.72015238e-9)
        self.assertAlmostEqual(result, 0.13619, places=5)


class Test_WiFi_Channel_Gain(unittest.TestCase):
    def test_normal_case(self):
        result = Formula.wifi_channel_gain(h_r=1, L_d=20)
        self.assertAlmostEqual(result, 0.1, places=1)

class TestLargeScaleFadingLoss(unittest.TestCase):
    def test_output_type(self):
        """Test if the output is a float"""
        np.random.seed(0)
        result = Formula.large_scale_fading_loss(10)
        self.assertIsInstance(result, float)

    def test_reasonable_output_range(self):
        """Check if the output is within a reasonable range for d=10"""
        np.random.seed(0)
        result = Formula.large_scale_fading_loss(10)
        expected_path_loss = 68 + 10 * 1.6 * math.log10(10 / 1)  # without shadowing
        self.assertTrue(expected_path_loss - 10 <= result <= expected_path_loss + 10)

    def test_repeatability_with_seed(self):
        """Ensure reproducibility when seed is fixed"""
        np.random.seed(42)
        val1 = Formula.large_scale_fading_loss(100)
        np.random.seed(42)
        val2 = Formula.large_scale_fading_loss(100)
        self.assertAlmostEqual(val1, val2, places=6)

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