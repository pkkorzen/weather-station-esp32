import urequests

IFTTT_URL = '/trigger/bme280_readings/with/key/YOUR_API_KEY'
SERVER = 'maker.ifttt.com'

class IFTTT:
    
    def __init__(self, ifttt_url=IFTTT_URL, server=SERVER):
        self.ifttt_url = ifttt_url
        self.server = server
    
    def make_ifttt_request(self, readings):
        print('Connecting to', self.server)
        json_data = '{"value1":"outside:' + readings[0] + ', inside:' + readings[1]+ '","value2":"' + readings[2] + '; index:' + readings[3] + \
        '","value3":"' + readings[4] + '"}'
        headers = {'Content-Type': 'application/json'}
        response = urequests.post('https://' + self.server + self.ifttt_url, data=json_data, headers=headers)
        print('Response:', response.content.decode())
        response.close()
        print('Closing Connection')