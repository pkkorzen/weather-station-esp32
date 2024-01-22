import urequests

CT8_URL = 'YOUR_URL'
SERVER = 'YOUR_SERVER'
API_KEY_VALUE = "API_KEY_VALUE"

class ExceptionLogger:
    
    def __init__(self, ct8_url=CT8_URL, server=SERVER):
        self.ct8_url = ct8_url
        self.server = server
    
    def log_exception(self, exception):
        print('Connecting to', self.server)
        httpRequestData = 'api_key=' + API_KEY_VALUE + '&exception=' + str(exception)
        
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = urequests.post('https://' + self.server + self.ct8_url, data=httpRequestData, headers=headers)
        print('Response:', response.content.decode())
        response.close()
        print('Closing Connection')
