import requests
import jwt
import json
from datetime import datetime, timedelta
import logging
import time

"""
More information on Zoom API's can be found at:
API documentation
https://marketplace.zoom.us/docs/api-reference/introduction

SDK Documentation
https://marketplace.zoom.us/docs/sdk/native-sdks/preface/introducing-zoom-sdk

Marketplace Documentation
https://marketplace.zoom.us/docs

Developer Forum
https://devforum.zoom.us/

Zoom Github
https://github.com/zoom
"""

####################################
#    CONFIGURE VARIABLES           #
####################################
"""
Change the variables in this section using you API_KEY and SECRET from the Zoom Marketplace https://marketplace.zoom.us
JWT_EXPIRY should be an Integer in seconds
DO NOT change the base URL
"""
API_KEY = "YOUR API KEY"
API_SECRET = "YOUR API SECRET"
JWT_EXPIRY = 60
BASE_URL = 'https://api.zoom.us/v2/'


####################################
#    CONFIGURE LOGGING             #
####################################
"""
This configuration will save a log file into the same folder as the *.py file
"""
logging.basicConfig(filename='logfile.log',level=logging.DEBUG, format='%(levelname)s %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

###########################################
# DO NOT CHANGE ANYTHING BELOW THIS LINE  #
###########################################

# Function to create JWT Token

def jwt_token():
    exp_time = datetime.utcnow() + timedelta(seconds =JWT_EXPIRY)
    payload = {'iss' : API_KEY, 'exp' : exp_time}
    headers = {'alg' : 'HS256', 'typ' : 'JWT'}
    token = str(jwt.encode(headers = headers, payload = payload, key = API_SECRET, algorithm = 'HS256'), 'utf-8')
    return(token)

# REQUEST FUNCTIONS

"""
Get JWT token, assemble headers, assemble endpoint URL, Log URL and Headers, send get request.
If status is not 200 log warning otherwise log response content as info
return response content
"""
def send_get_request(endpoint):
    token = jwt_token()
    headers  = {"authorization" : "Bearer %s" % token, "content-type" : "application/json"}
    FINAL_URL = BASE_URL + endpoint
    logging.debug("'{0}', '{1}'".format(FINAL_URL, headers))
    r = requests.get(FINAL_URL, headers = headers)
    if r.status_code != 200:
        logging.warning("'{0}'".format(r.content))
    logging.info("'{0}'".format(r.content))
    return r.content



def list_users():
    logging.info('list_users')
    url = '/users'
    user_list = []
    response = send_get_request(url)
    encoded_data=json.loads(response)
    for item in encoded_data['users']:
        user = item['id']
        user_list.append(user)
    return(user_list)

def get_meetings(userID):
    logging.info('get meetings: %s' % userID)
    url = '/users/%s/meetings' % userID
    response = send_get_request(url)
    return(response)

def get_all_meetings():
    logging.info('get all meetings')
    user_list = list_users()
    date_format = "%Y-%m-%dT%H:%M:%SZ"
    for user in user_list:
        meetings = get_meetings(user)
        encoded_data=json.loads(meetings)
        for item in encoded_data['meetings']:
            meeting_type = item['type']
            if meeting_type == '2':
                mstart_time = item['start_time']
                ftime = datetime.strptime(mstart_time, date_format)
                if ftime > datetime.now():
                    print(item)
        time.sleep(.300)

get_all_meetings()