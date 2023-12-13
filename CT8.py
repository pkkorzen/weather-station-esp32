import urequests

CT8_URL = '/esp-post-data.php'
SERVER = 'pogodynka.ct8.pl'
API_KEY_VALUE = "API_KEY_VALUE"
class CT8:
    
    def __init__(self, ct8_url=CT8_URL, server=SERVER):
        self.ct8_url = ct8_url
        self.server = server
    
    def make_ct8_request(self, readings):
        print('Connecting to', self.server)
        httpRequestData = 'api_key=' + API_KEY_VALUE + '&outside_temp=' + str(readings[0][0])
        + '&inside_temp=' + str(readings[1][0]) + '&outside_hum=' + str(readings[0][2])
        + '&inside_hum=' + str(readings[1][2]) + '&outside_pres=' + str(readings[0][1])
        + '&inside_pres=' + str(readings[1][1]) + '&eaqi_index=' + str(readings[3])
        + '&pms_1=' + str(readings[2][0]) + '&pms_2_5=' + str(readings[2][1])
        + '&pms_10=' + str(readings[2][2]) + '&sht30_temp=' + str(readings[4][0])
        + '&sht30_hum=' + str(readings[4][1]) + ""
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = urequests.post('https://' + self.server + self.ct8_url, data=httpRequestData, headers=headers)
        print('Response:', response.content.decode())
        response.close()
        print('Closing Connection')
