from machine import SoftI2C, Pin
import time

__version__ = '0.2.3'
__author__ = 'Roberto Sánchez'
__license__ = "Apache License 2.0. https://www.apache.org/licenses/LICENSE-2.0"

# I2C address B 0x45 ADDR (pin 2) connected to VDD
DEFAULT_I2C_ADDRESS = 0x44


class SHT30:
    """
    SHT30 sensor driver in pure python based on I2C bus

    References:
    * https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/2_Humidity_Sensors/Sensirion_Humidity_Sensors_SHT3x_Datasheet_digital.pdf  # NOQA
    * https://www.wemos.cc/sites/default/files/2016-11/SHT30-DIS_datasheet.pdf
    * https://github.com/wemos/WEMOS_SHT3x_Arduino_Library
    * https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/11_Sample_Codes_Software/Humidity_Sensors/Sensirion_Humidity_Sensors_SHT3x_Sample_Code_V2.pdf
    """
    POLYNOMIAL = 0x131  # P(x) = x^8 + x^5 + x^4 + 1 = 100110001

    ALERT_PENDING_MASK = 0x8000     # 15
    HEATER_MASK = 0x2000            # 13
    RH_ALERT_MASK = 0x0800          # 11
    T_ALERT_MASK = 0x0400           # 10
    RESET_MASK = 0x0010             # 4
    CMD_STATUS_MASK = 0x0002        # 1
    WRITE_STATUS_MASK = 0x0001      # 0

    # MSB = 0x2C LSB = 0x06 Repeatability = High, Clock stretching = enabled
    MEASURE_CMD = b'\x2C\x10'
    STATUS_CMD = b'\xF3\x2D'
    RESET_CMD = b'\x30\xA2'
    CLEAR_STATUS_CMD = b'\x30\x41'
    ENABLE_HEATER_CMD = b'\x30\x6D'
    DISABLE_HEATER_CMD = b'\x30\x66'
    READ_HIGH_ALERT_LIMIT_SET_CMD = b'\xE1\x1F'
    READ_HIGH_ALERT_LIMIT_CLEAR_CMD = b'\xE1\x14'
    READ_LOW_ALERT_LIMIT_SET_CMD = b'\xE1\x09'
    READ_LOW_ALERT_LIMIT_CLEAR_CMD = b'\xE1\x02'
    WRITE_HIGH_ALERT_LIMIT_SET_CMD = b'\x61\x1D'
    WRITE_HIGH_ALERT_LIMIT_CLEAR_CMD = b'\x61\x16'
    WRITE_LOW_ALERT_LIMIT_SET_CMD = b'\x61\x0B'
    WRITE_LOW_ALERT_LIMIT_CLEAR_CMD = b'\x61\x00'
    PER_HIGH_REP_05_HZ_CMD = b'\x20\x32'
    PER_MED_REP_05_HZ_CMD    = b'\x20\x24'
    PER_LOW_REP_05_HZ_CMD   = b'\x20\x2F'
    PER_HIGH_REP_1_HZ_CMD       = b'\x21\x30'
    PER_MED_REP_1_HZ_CMD       = b'\x21\x26'
    PER_LOW_REP_1_HZ_CMD       = b'\x21\x2D'
    PER_HIGH_REP_2_HZ_CMD       = b'\x22\x36'
    PER_MED_REP_2_HZ_CMD       = b'\x22\x20'
    PER_LOW_REP_2_HZ_CMD       = b'\x22\x2B'
    PER_HIGH_REP_4_HZ_CMD       = b'\x23\x34'
    PER_MED_REP_4_HZ_CMD       = b'\x23\x22'
    PER_LOW_REP_4_HZ_CMD       = b'\x23\x29'
    PER_HIGH_REP_10_HZ_CMD      = b'\x27\x37'
    PER_MED_REP_10_HZ_CMD      = b'\x27\x21'
    PER_LOW_REP_10_HZ_CMD      = b'\x27\x2A'
    FETCH_DATA_CMD = b'\xE0\x00'
    STOP_PERIODIC_MODE_CMD = b'x30\x93'

    def __init__(self, scl_pin=32, sda_pin=33, delta_temp=0, delta_hum=0, i2c_address=DEFAULT_I2C_ADDRESS):
        self.i2c = SoftI2C(scl=Pin(scl_pin), sda=Pin(sda_pin))
        self.i2c_addr = i2c_address
        self.set_delta(delta_temp, delta_hum)
        time.sleep_ms(50)

    def init(self, scl_pin=32, sda_pin=33):
        """
        Init the I2C bus using the new pin values
        """
        self.i2c.init(scl=Pin(scl_pin), sda=Pin(sda_pin))

    def is_present(self):
        """
        Return true if the sensor is correctly conneced, False otherwise
        """
        return self.i2c_addr in self.i2c.scan()

    def set_delta(self, delta_temp=0, delta_hum=0):
        """
        Apply a delta value on the future measurements of temperature and/or humidity
        The units are Celsius for temperature and percent for humidity (can be negative values)
        """
        self.delta_temp = delta_temp
        self.delta_hum = delta_hum

    def _check_crc(self, data):
        # calculates 8-Bit checksum with given polynomial
        crc = 0xFF

        for b in data[:-1]:
            crc ^= b
            for _ in range(8, 0, -1):
                if crc & 0x80:
                    crc = (crc << 1) ^ SHT30.POLYNOMIAL
                else:
                    crc <<= 1
        crc_to_check = data[-1]
        return crc_to_check == crc

    def send_cmd(self, cmd_request, response_size=6, read_delay_ms=100):
        """
        Send a command to the sensor and read (optionally) the response
        The responsed data is validated by CRC
        """
        try:
            self.i2c.start()
            self.i2c.writeto(self.i2c_addr, cmd_request)
            if not response_size:
                self.i2c.stop()
                return
            time.sleep_ms(read_delay_ms)
            data = self.i2c.readfrom(self.i2c_addr, response_size)
            self.i2c.stop()
            for i in range(response_size//3):
                if not self._check_crc(data[i*3:(i+1)*3]):  # pos 2 and 5 are CRC
                    raise SHT30Error(SHT30Error.CRC_ERROR)
            if data == bytearray(response_size):
                raise SHT30Error(SHT30Error.DATA_ERROR)
            return data
        except OSError as ex:
            if 'I2C' in ex.args[0]:
                raise SHT30Error(SHT30Error.BUS_ERROR)
            raise ex

    def clear_status(self):
        """
        Clear the status register
        """
        return self.send_cmd(SHT30.CLEAR_STATUS_CMD, None)

    def reset(self):
        """
        Send a soft-reset to the sensor
        """
        return self.send_cmd(SHT30.RESET_CMD, None)

    def status(self, raw=False):
        """
        Get the sensor status register.
        It returns a int value or the bytearray(3) if raw==True
        """
        data = self.send_cmd(SHT30.STATUS_CMD, 3, read_delay_ms=20)

        if raw:
            return data

        status_register = (data[0] << 8) | data[1]
        return status_register

    def measure(self, raw=False):
        """
        If raw==True returns a bytearrya(6) with sensor direct measurement otherwise
        It gets the temperature (T) and humidity (RH) measurement and return them.

        The units are Celsius and percent
        """
        data = self.send_cmd(SHT30.MEASURE_CMD, 6)

        if raw:
            return data

        t_celsius = (((data[0] << 8 |  data[1]) * 175) / 0xFFFF) - 45 + self.delta_temp
        rh = (((data[3] << 8 | data[4]) * 100.0) / 0xFFFF) + self.delta_hum
        return t_celsius, rh

    def measure_int(self, raw=False):
        """
        Get the temperature (T) and humidity (RH) measurement using integers.
        If raw==True returns a bytearrya(6) with sensor direct measurement otherwise
        It returns a tuple with 4 values: T integer, T decimal, H integer, H decimal
        For instance to return T=24.0512 and RH= 34.662 This method will return
        (24, 5, 34, 66) Only 2 decimal digits are returned, .05 becomes 5
        Delta values are not applied in this method
        The units are Celsius and percent.
        """
        data = self.send_cmd(SHT30.MEASURE_CMD, 6)
        if raw:
            return data
        aux = (data[0] << 8 | data[1]) * 175
        t_int = (aux // 0xffff) - 45
        t_dec = (aux % 0xffff * 100) // 0xffff
        aux = (data[3] << 8 | data[4]) * 100
        h_int = aux // 0xffff
        h_dec = (aux % 0xffff * 100) // 0xffff
        return t_int, t_dec, h_int, h_dec
        
    def read_alert_state(self):
        time.sleep(0.001)
        register_raw = self.status()
        if(((register_raw & SHT30.RH_ALERT_MASK) >> 11 == 1)or((register_raw & SHT30.T_ALERT_MASK) >> 10 == 1)):
          return True
        else:
          return False
    
    def start_periodic(self):
        self.send_cmd(SHT30.PER_HIGH_REP_05_HZ_CMD, 0)
        
    def stop_periodic(self):
        self.send_cmd(SHT30.STOP_PERIODIC_MODE_CMD, 0)
        
    def fetch_data(self):
        raw_data = self.send_cmd(SHT30.FETCH_DATA_CMD, 6)
        temp_raw_data= [raw_data[0],raw_data[1],raw_data[2]]
        hum_raw_data= [raw_data[3],raw_data[4],raw_data[5]]
        hum = self.convert_raw_humidity(hum_raw_data)
        temp = self.convert_raw_temperature(temp_raw_data)
        return temp, hum
        
    def read_high_alert_limit_set(self):
        raw_data = self.send_cmd(SHT30.READ_HIGH_ALERT_LIMIT_SET_CMD, 3)
        return self.calculate_alert_values(raw_data)
    
    def read_high_alert_limit_clear(self):
        raw_data = self.send_cmd(SHT30.READ_HIGH_ALERT_LIMIT_CLEAR_CMD, 3)
        return self.calculate_alert_values(raw_data)
        
    def read_low_alert_limit_set(self):
        raw_data = self.send_cmd(SHT30.READ_LOW_ALERT_LIMIT_SET_CMD, 3)
        return self.calculate_alert_values(raw_data)
    
    def read_low_alert_limit_clear(self):
        raw_data = self.send_cmd(SHT30.READ_LOW_ALERT_LIMIT_CLEAR_CMD, 3)
        return self.calculate_alert_values(raw_data)
    
    def write_high_alert_limit_set(self, temperature, humidity):
        return self.write_alert_data(temperature, humidity, SHT30.WRITE_HIGH_ALERT_LIMIT_SET_CMD)
    
    def write_high_alert_limit_clear(self, temperature, humidity):
        return self.write_alert_data(temperature, humidity, SHT30.WRITE_HIGH_ALERT_LIMIT_CLEAR_CMD)
        
    def write_low_alert_limit_set(self, temperature, humidity):
        return self.write_alert_data(temperature, humidity, SHT30.WRITE_LOW_ALERT_LIMIT_SET_CMD)
    
    def write_low_alert_limit_clear(self, temperature, humidity):
        return self.write_alert_data(temperature, humidity, SHT30.WRITE_LOW_ALERT_LIMIT_CLEAR_CMD)
    
    def write_alert_data(self, temperature, humidity, SHT30command):
        rawHumidity = self.calculate_raw_humidity(humidity)
        rawTemperature = self.calculate_raw_temperature(temperature)
        raw_data = (rawHumidity & 0xFE00) | ((rawTemperature >> 7) & 0x001FF)
        buf = []
        buf.append(raw_data >> 8);
        buf.append(raw_data & 0xFF);
        command = SHT30command
        command += self.convert_to_hex(buf)
        checksum = self.check_crc(buf)
        command += checksum.to_bytes(1, 'big', False)
        raw_data = self.send_cmd(command, None)
        return True
        
    def calculate_alert_values(self, raw_data):
        hum = self.calculate_humidity(raw_data)
        temp = self.calculate_temperature(raw_data)
        return temp, hum
    
    def calculate_humidity(self, raw_data):
        humRaw = self.recreate_alert_limits_data_format(raw_data)
        humRaw = humRaw & 0xFE00
        humRaw = humRaw | 0xCD
        return round((100.0 * humRaw / 65535), 2)
        
    def calculate_temperature(self, raw_data):
        tempRaw = self.recreate_alert_limits_data_format(raw_data)
        tempRaw = tempRaw << 7
        tempRaw = tempRaw & 0xFF80
        tempRaw = tempRaw | 0x1A
        return round((175 * tempRaw / 65535 - 45), 2)
    
    def convert_raw_temperature(self,raw_temperature):
        raw_value = raw_temperature[0]
        raw_value = (raw_value << 8) | raw_temperature[1]
        return 175.0 * raw_value / 65535 - 45
    
    def convert_raw_humidity(self,raw_humidity):
        raw_value = raw_humidity[0]
        raw_value = (raw_value << 8) | raw_humidity[1]
        return 100.0 * raw_value / 65535
        
    def calculate_raw_humidity(self, value):
        return int(value / 100.0 * 65535.0)
    
    def calculate_raw_temperature(self, value):
        return int((value + 45.0) / 175.0 * 65535.0)
        
    def check_crc(self,data):
        crc = 0xFF
        for i in range(0,2):
            crc = crc^data[i]
            for bit in range(0,8):
                if(crc&0x80):
                    crc = ((crc <<1)^0x31)
                else:
                    crc = (crc<<1)
        crc = crc&0xFF
        return crc
        
    def recreate_alert_limits_data_format(self,raw_data):
        data = raw_data[0]
        data = data << 8 | raw_data[1]
        return data
    
    def convert_to_hex(self, data):
        command = data[0].to_bytes(1, 'big', False)
        command += data[1].to_bytes(1, 'big', False)
        return command
    
    def convert_to_hex2(self, data):
        command = data.to_bytes(1, 'big', False)
        return command

class SHT30Error(Exception):
    """
    Custom exception for errors on sensor management
    """
    BUS_ERROR = 0x01
    DATA_ERROR = 0x02
    CRC_ERROR = 0x03

    def __init__(self, error_code=None):
        self.error_code = error_code
        super().__init__(self.get_message())

    def get_message(self):
        if self.error_code == SHT30Error.BUS_ERROR:
            return "Bus error"
        elif self.error_code == SHT30Error.DATA_ERROR:
            return "Data error"
        elif self.error_code == SHT30Error.CRC_ERROR:
            return "CRC error"
        else:
            return "Unknown error"

