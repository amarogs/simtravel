# -*- coding: utf-8 -*-
class Units():
    def __init__(self, speed=10, cell_length=5, simulation_speed=1, battery=24, cs_power=7, autonomy=135):
        """
        Recibes the simulation units:
        :param speed: is the actual speed measured in (km/h)
        :param cell_length: is the actual length of a cell measured in (m/cell)
        :param simulation_speed: is the speed (cell/step) of the simulation
        :param battery: is the capacity of the battery measured in kWh.
        :param cs_power: is the charging station power output measured in kW
        :param autonomy: is the number of km that can be made using a full charge in km.

        step is the simulation unit for time.
        cell is the simulation unit for length.
        All units and conversiones are returned in float.

        By default, the speed is 10km/h (10**4/3600), 
        cell_length is 5m and simulation speed is 1 cell/step

           """
        super().__init__()
        self.speed = (speed * 10**3)/3600  # (m/s)
        self.cell_length = cell_length  # (m/cell)
        self.simulation_speed = simulation_speed  # (cell/step)
        self.battery = (3.6*10**6) * battery  # (J)
        self.cs_power = cs_power * 10**3  # (J/s)
        self.time_fully_charge = self.battery/self.cs_power  # (s)
        self.autonomy = (autonomy * 10**3) * (1/self.cell_length)  # (cell)
        self.step_to_s = float(
            (cell_length * simulation_speed) / speed)  # (s/ step)
        self.cs_step_to_cell = (
            self.time_fully_charge/self.step_to_s) / self.autonomy  # (step / cell)

    def seconds_to_hours(self, seconds):
        """1 hour is 3600 seconds """
        return seconds/3600

    def meters_to_km(self, meters):
        """1km is 1000 meters """
        return meters/1000

    def steps_to_meters(self, steps):
        """Given a number of steps, returns the equivalent
        in meters """
        return self.cell_length * self.simulation_speed * steps

    def cells_to_meters(self, cells):
        """Given a number of cells, returns the equivalent
        in meters"""
        return self.cell_length * cells

    def steps_to_seconds(self, steps):
        """Given a number of steps, returns the equivalent
        in seconds """
        return self.step_to_s * steps

    def minutes_to_steps(self, minutes):
        """Given a number of minutes, returns the equivalent
        in steps of the simulation."""
        return minutes*60/self.step_to_s

    def steps_to_recharge(self,cells):
        """Given a number of cells returns the 
        steps needed to recharge that amount."""
        return self.cs_step_to_cell * cells

    def seconds_to_recharge(self,cells):
        """Given a number of cells returns the
        seconds needed to recharge that amount """
        return self.steps_to_second(self.cs_step_to_cell * cells)
