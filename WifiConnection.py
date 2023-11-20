import network

SSID = 'ssid'
PASSWORD = 'password'

class WifiConnection:

    def __init__(self, ssid=SSID, password=PASSWORD):
        self.ssid = ssid
        self.password = password

    def connect_wifi(self):
        # Connect to your network
        station = network.WLAN(network.STA_IF)
        station.active(True)
        station.connect(self.ssid, self.password)
        while station.isconnected() == False:
            pass
        print('Connection successful')
        print(station.ifconfig())