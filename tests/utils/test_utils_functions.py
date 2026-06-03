import unittest
from utils.utils import format_sensor_name

class TestUtilsFunctions(unittest.TestCase):
    def test_format_sensor_name(self):
        """Test the format_sensor_name function with various inputs."""
        # Happy paths (single underscore)
        self.assertEqual(format_sensor_name("sensor_1"), "Sensor 1")
        self.assertEqual(format_sensor_name("Sensor_2"), "Sensor 2")
        self.assertEqual(format_sensor_name("my_sensor_3"), "Sensor sensor")

        # Cases without underscore
        self.assertEqual(format_sensor_name("sensor"), "sensor")
        self.assertEqual(format_sensor_name("sensor1"), "sensor1")

        # Cases with multiple underscores
        self.assertEqual(format_sensor_name("sensor_1_a"), "Sensor 1")

        # Edge cases
        self.assertEqual(format_sensor_name(""), "")
        self.assertEqual(format_sensor_name("_"), "Sensor ")
        self.assertEqual(format_sensor_name(" "), " ")

if __name__ == "__main__":
    unittest.main()
