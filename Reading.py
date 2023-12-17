from sht30_ext_refactor import SHT30
import bme280
from pms7003 import Pms7003
from machine import Pin, SoftI2C
from EAQI import EAQI
from time import sleep

I2C=SoftI2C(scl=Pin(22), sda=Pin(21))
I2C2=SoftI2C(scl=Pin(32), sda=Pin(33))

# measurement_list_1 = [0,0,0,0]
# measurement_list_2_5 = [0,0,0,0]
# measurement_list_10 = [0,0,0,0]

class Reading():

    def __init__(self, i2c=I2C, i2c2=I2C2, measurements_per_hour=4):
        self.i2c = i2c
        self.i2c2 = i2c2

        self.measurements_per_hour = measurements_per_hour

        self.measurement_list_1 = [0] * self.measurements_per_hour
        self.measurement_list_2_5 = [0] * self.measurements_per_hour
        self.measurement_list_10 = [0] * self.measurements_per_hour

        self.sht30_sensor = SHT30()
        sleep(1)
        self.sht30_sensor.reset()
        sleep(1)
        self.sht30_sensor.clear_status() #clears alert pending pin no. 15
        sleep(1)
        self.sht30_sensor.start_periodic()
        sleep(1)
        self.bme280_inside = bme280.BME280(i2c=self.i2c)
        sleep(1)
        self.bme280_outside = bme280.BME280(i2c=self.i2c2)
        sleep(1)
        self.pms7003 = Pms7003(uart=2)

    def get_air_quality_readings(self):
        return self.pms7003.read()
    
    def get_periodic_air_quality_readings(self):
        return sum(self.measurement_list_1) / self.measurements_per_hour, sum(self.measurement_list_2_5) / self.measurements_per_hour, sum(self.measurement_list_10) / self.measurements_per_hour
    
    def get_outside_readings(self):
        return self.bme280_outside.values()
    
    def get_inside_readings(self):
        return self.bme280_inside.values()
    
    def get_heater_chamber_readings(self):
        return self.sht30_sensor.fetch_data()
    
    def calculate_air_quality_index(self):
        return EAQI.eaqi(self.get_periodic_air_quality_readings()[1], self.get_periodic_air_quality_readings()[2])
    
    def get_all_readings(self):
        return self.get_outside_readings(), self.get_inside_readings(), self.get_periodic_air_quality_readings(), self.calculate_air_quality_index(), self.get_heater_chamber_readings()
    
    def add_air_quality_readings_to_periodic_lists(self, measurement_counter):
        del self.measurement_list_1[measurement_counter]
        self.measurement_list_1.insert(measurement_counter, self.get_air_quality_readings()['PM1_0_ATM'])

        del self.measurement_list_2_5[measurement_counter]
        self.measurement_list_2_5.insert(measurement_counter, self.get_air_quality_readings()['PM2_5_ATM'])
        
        del self.measurement_list_10[measurement_counter]
        self.measurement_list_10.insert(measurement_counter, self.get_air_quality_readings()['PM10_0_ATM'])