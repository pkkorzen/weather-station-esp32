import urequests

IFTTT_URL = '/trigger/bme280_readings/with/key/YOUR_API_KEY'
SERVER = 'maker.ifttt.com'

class IFTTT:
    
    def __init__(self, ifttt_url=IFTTT_URL, server=SERVER):
        self.ifttt_url = ifttt_url
        self.server = server
    
    def make_ifttt_request(self, readings):
        print('Connecting to', self.server)
        json_data = '{"value1":"' + readings[0][0] + '","value2":"' + readings[0][1]  + \
        '","value3":"' + readings[0][2] + '","value4":"' + readings[1][0] + '","value5":"' + readings[1][1]  + \
        '","value6":"' + readings[1][2] + '","value7":"' + readings[2][0] + '","value8":"' + readings[2][1]  + \
        '","value9":"' + readings[2][2] + '","value10":"' + readings[3] + '","value11":"' + readings[4][0]  + \
        '","value12":"' + readings[4][1] + '"}'
        headers = {'Content-Type': 'application/json'}
        response = urequests.post('https://' + self.server + self.ifttt_url, data=json_data, headers=headers)
        print('Response:', response.content.decode())
        response.close()
        print('Closing Connection')