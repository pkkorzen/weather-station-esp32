import socket

class WebServer:

    def web_page(readings):
        html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="icon" href="data:,"><style>body { text-align: center; font-family: "Trebuchet MS", Arial;}
        table { border-collapse: collapse; width:35%; margin-left:auto; margin-right:auto; }
        th { padding: 12px; background-color: #0043af; color: white; }
        tr { border: 1px solid #ddd; padding: 12px; }
        tr:hover { background-color: #bcbcbc; }
        td { border: none; padding: 12px; }
        .sensor { color:white; font-weight: bold; background-color: #bcbcbc; padding: 1px;
        </style></head><body><h1>ESP with BME280</h1>
        <table><tr><th>MEASUREMENT</th><th>VALUE</th></tr>
        <tr><td>Temperature (outside)</td><td><span class="sensor">""" + str(readings[0][0]) + """</span></td></tr>
        <tr><td>Pressure (outside)</td><td><span class="sensor">""" + str(readings[0][1]) + """</span></td></tr>
        <tr><td>Humidity (outside)</td><td><span class="sensor">""" + str(readings[0][2]) + """</span></td></tr>
        <tr><td>Temperature (inside)</td><td><span class="sensor">""" + str(readings[1][0]) + """</span></td></tr>
        <tr><td>Pressure (inside)</td><td><span class="sensor">""" + str(readings[1][1]) + """</span></td></tr>
        <tr><td>Humidity (inside)</td><td><span class="sensor">""" + str(readings[1][2]) + """</span></td></tr>
        <tr><td>Particles 1.0 (hourly)</td><td><span class="sensor">""" + str(readings[2][0]) + """</span></td></tr>
        <tr><td>Particles 2.5 (hourly)</td><td><span class="sensor">""" + str(readings[2][1]) + """</span></td></tr>
        <tr><td>Particles 10.0 (hourly)</td><td><span class="sensor">""" + str(readings[2][2]) + """</span></td></tr>
        <tr><td>European air quality index</td><td><span class="sensor">""" + str(readings[3]) + """</span></td></tr>
        <tr><td>Heater chamber temperature</td><td><span class="sensor">""" + str(readings[4][0]) + """</span></td></tr>
        <tr><td>Heater chamber humidity</td><td><span class="sensor">""" + str(readings[4][1]) + """</span></td></tr></body></html>"""
        return str(html)
    
    def open_socket(self):
        # Open a socket
        address = ('', 80)
        self.connection = socket.socket()
        self.connection.bind(address)
        self.connection.listen(1)
    
    def serve(self, reading):
        
        #Start a web server
        client, addr = self.connection.accept()
        client.settimeout(3.0)
        print('Got a connection from %s' % str(addr))
        request = client.recv(1024)
        client.settimeout(None)
        request = str(request)
        print('Content = %s' % request)
        html = self.web_page(reading.get_all_readings())
        client.send(html)
        client.close()
        print('Connection closed')