import unittest

from src.metrics.units import Units

class TestUnitsModule(unittest.TestCase):

    def test_seconds_to_hours(self):
        units = Units(speed=10, cell_length=5, simulation_speed=1, battery=24, cs_power=7, autonomy=135)
        self.assertEqual(units.seconds_to_hours(3600),1.0, "Wrong units conversion to hours")

    def test_meter_to_km(self):
        units = Units(speed=10, cell_length=5, simulation_speed=1, battery=24, cs_power=7, autonomy=135)
        self.assertEqual(units.meters_to_km(1000), 1.0, "Wrong converesion to km")
    
    def test_steps_to_meters(self):
        units = Units(speed=10, cell_length=5, simulation_speed=1, battery=24, cs_power=7, autonomy=135)
        self.assertEqual(units.steps_to_meters(10), 50, "Wrong conversion simulation steps to meters")
    def test_cells_to_meters(self):
        units = Units(speed=10, cell_length=5, simulation_speed=1, battery=24, cs_power=7, autonomy=135)
        self.assertEqual(units.cells_to_meters(10), 50, "Wrong conversion from cell to meters")
    def test_steps_to_seconds(self):
        units = Units(speed=10, cell_length=5, simulation_speed=1, battery=24, cs_power=7, autonomy=135)
        self.assertEqual(units.steps_to_seconds(10), 18.0, "Wrong conversion steps to seconds")
    def test_steps_to_minutes(self):
        units = Units(speed=10, cell_length=5, simulation_speed=1, battery=24, cs_power=7, autonomy=135)
        self.assertEqual(units.steps_to_minutes(20), 0.6, "Wrong conversion from steps to minutes")
    def test_minutes_to_steps(self):
        units = Units(speed=10, cell_length=5, simulation_speed=1, battery=24, cs_power=7, autonomy=135)
        self.assertEqual(units.minutes_to_steps(0.6), 20.0, "Wrong conversion from minutes to steps")
    def test_steps_to_recharge(self):
        units = Units(speed=10, cell_length=5, simulation_speed=1, battery=24, cs_power=7, autonomy=135)
        d = 1.8*27000
        n = 10 * (((3.6*10**6) * 24 )/ 7000 )
        self.assertEqual(round(units.steps_to_recharge(10),5), round(n/d, 5), "Wrong computation of the steps to recharge")
    
    def test_simulation_speed_to_kmh(self):
        units = Units(speed=10, cell_length=5, simulation_speed=1, battery=24, cs_power=7, autonomy=135)
        self.assertEqual(units.simulation_speed_to_kmh(1), 10, "Wrong conversion from sim speed to real speed")
    def tests_step_to_s(self):
        units = Units(speed=10, cell_length=5, simulation_speed=1, battery=24, cs_power=7, autonomy=135)
        self.assertEqual(units.step_to_s, 1.8, "Wrong constant value for converting steps to seconds")