import requests
import jwt
import json
import config
from datetime import datetime, timedelta
import csv
import string
import logging

#confiigure variables
"""
Change the variables in this secction using you API_KEY and SECRET from the Zoom Marketplace
JWT_EXPIRY should be an Integer in seconds
DOMAIN should be a domain you own
"""
API_KEY = config.API_KEY
API_SECRET = config.API_SECRET
JWT_EXPIRY = 60
BASE_URL = 'https://api.zoom.us/v2/'
DOMAIN = '@wearewright.com'

#Configure Logging
logging.basicConfig(filename='logfile.log',level=logging.DEBUG, format='%(levelname)s %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# DUMMY DATA TO CREATE SUBS
"""
This data can be used to create Sub Accounts for testing purposes
Call the create_sub_account() function to create accounts
"""
sub_accounts = {'accounts' : [{"first_name" : "Test1", "last_name" : "Sub1", "email" : "test1%s" % DOMAIN, "password" : "Sub1pwd123!"},
                            {"first_name" : "Test2", "last_name" : "Sub2", "email" : "test2%s" % DOMAIN, "password" : "Sub2pwd123!"},
                            {"first_name" : "Test3", "last_name" : "Sub3", "email" : "test3%s" % DOMAIN, "password" : "Sub3pwd123!"},
                            {"first_name" : "Test4", "last_name" : "Sub4", "email" : "test4%s" % DOMAIN, "password" : "Sub4pwd123!"}
                            ]
                }
# DUMMY DATA TO CREATE GROUPS
"""
This data can be used to create groups to propogate across your sub-accounts
"""
group_list = ['group1', 'group2', 'group3']

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

def send_patch_request(endpoint, data):
    token = jwt_token()
    headers  = {'authorization' : 'Bearer %s' % token, 'content-type' : 'application/json'}
    FINAL_URL = BASE_URL + endpoint
    logging.debug("'{0}', '{1}', '{2}'".format(FINAL_URL, headers, data))
    r = requests.patch(FINAL_URL, headers = headers, data = data)
    if r.status_code != 200:
        logging.warning("'{0}'".format(r.content))
    logging.info("'{0}'".format(r.content))
    return r.content

def send_post_request(endpoint, data):
    token = jwt_token()
    headers  = {'authorization' : 'Bearer %s' % token, 'content-type' : 'application/json'}
    FINAL_URL = BASE_URL + endpoint
    logging.debug("'{0}', '{1}', '{2}'".format(FINAL_URL, headers, data))
    r = requests.post(FINAL_URL, headers = headers, data = data)
    if r.status_code != 200:
        logging.warning("'{0}'".format(r.content))
    logging.info("'{0}'".format(r.content))
    return r.content


#Account FUNCTIONS
def list_sub_accounts():
    logging.info("list_sub_accounts")
    accounts = []
    url = '/accounts'
    response = send_get_request(url)
    encoded_data=json.loads(response)
    for item in encoded_data['accounts']:
        accountID = item['id']
        accounts.append(accountID)
        print(accountID)
    return(accounts)


def get_account_settings(accountID):
    logging.info("Get Account Settings")
    url = '/accounts/%s/settings' % accountID
    #print(url)
    response = send_get_request(url)
    data = response
    encoded_data = json.loads(data)
    #print(encoded_data)
    return(encoded_data)

def update_account_settings(accountID, payload):
    logging.info("Update Account Settings: %s" % accountID)
    url = '/accounts/%s/settings' % accountID
    data = payload
    response = send_patch_request(url, json.dumps(data))
    print(response)
    return(response)

def get_locked_settings(accountID):
    logging.info("Get Locked Settings")
    url = "/accounts/%s/lock_settings" %accountID
    response = send_get_request(url)
    data = response
    encoded_data = json.loads(data)
    #print(encoded_data)
    return(encoded_data)

def update_sub_accounts(fromAccount):
    logging.info("Update Sub Accounts")
    account_list = list_sub_accounts()
    account_settings = get_account_settings(fromAccount)
    for account in account_list:
        response = update_account_settings(account, account_settings)
        print(response)

def update_locked_settings(accountID, payload):
    logging.info("Update Locked Settings: %s" % accountID)
    url = '/accounts/%s/settings' % accountID
    data = payload
    response = send_patch_request(url, json.dumps(data))
    print(response)
    return(response)

def update_sub_account_groups():
    logging.info("Update Sub Account Groups")
    account_list = list_sub_accounts()
    for account in account_list:
        groups = list_groups(account)
        for group in groups:
            response = create_group(account, group)
            print(response)

def create_sub_account():
    logging.info("Create Sub Account")
    for d in sub_accounts['accounts']:
        first_name = d['first_name']
        last_name = d['last_name']
        email = d['email']
        password = d['password']
        url = '/accounts'
        payload = {"first_name" : "%s" % first_name,
                    "last_name" : "%s" % last_name,
                    "email" : "%s" % email,
                    "password" : "%s" % password}
        print(payload)
        response = send_post_request(url, json.dumps(payload))
        print(response)

def propogate_account_settings(fromAccount):
    logging.info("Propogate Account Settings")
    account_list = list_sub_accounts()
    payload = get_account_settings(fromAccount)
    for account in account_list:
        response = update_account_settings(account, payload)
        print(response)

def propogate_locked_settings(fromAccount):
    logging.info("Propogate Locked Settings")
    account_list = list_sub_accounts()
    payload = get_locked_settings(fromAccount)
    for account in account_list:
        response = update_locked_settings(account, payload)
        print(response)

# Group Functions

def create_group(accountID, groupName):
    logging.info("Create Group")
    url = '/accounts/%s/groups' % accountID
    print(url)
    payload = {'name' : '%s' % groupName}
    response = send_post_request(url, json.dumps(payload))
    print(response)
    return(response)

#NEEDS TESTING
def list_groups(accountID):
    logging.info("List Groups")
    groups = []
    url = '/v2/accounts/%s/groups' % accountID
    response = send_get_request(url)
    print('response is : %s' % response)
    encoded_data=json.loads(response)
    for item in encoded_data['groups']:
        group = item['id']
        groups.append(group)
        print(group)
    print(groups)
    return(groups)

#NEEDS TESTTING
def get_group_settings(accountID, group):
    logging.info("Get Group Settings")
    url = '/accounts/%s/groups/%s/settings' % accountID, group
    response = send_get_request(url)
    return(response)

#NEEDS TESTING
def update_group_settings(accountID, group, payload):
    logging.info("Update Group Settings: %s : %s" % accountID, group)
    url = '/accounts/%s/groups/%s/settings' % accountID, group
    response = send_patch_request(url, json.dumps(payload))
    return(response)

#NEEDS TESTING
def propogate_group_settings(fromAccount):
    logging.info("Propogate Group Settings")
    account_list = list_sub_accounts()
    group_list = list_groups(fromAccount)
    for group in group_list:
        payload = get_group_settings(fromAccount, group)
        for account in account_list:
            response = update_group_settings(account, group, payload)
            print(response)
    

# REPORT FUNCTIONS

#NEEDS TESTING
def get_daily_report(accountID):
    logging.info("Get Daily Report")
    url = '/accounts/%s/report/daily' % accountID
    response = send_get_request(url)
    json_data = json.loads(response)
    csv_data = open('/reports/daily/%s.csv' % datetime.now)
    csvwriter = csv.writer(csv_data)
    count = 0
    for i in json_data['dates']:
        if count == 0:
            header = i.keys()
            csvwriter.writerow(header)
            count += 1
        csvwriter.writerow(i.values())
    csv_data.close

#NEEDS TESTING
def get_active_host_report(accountID):
    logging.info("Get Active Host Report")
    url = '/accounts/%s/report/users' % accountID
    response = send_get_request(url)
    json_data = json.loads(response)
    csv_data = open('/reports/users/%s.csv' % datetime.now)
    csvwriter = csv.writer(csv_data)
    count = 0
    for i in json_data['users']:
        if count == 0:
            header = i.keys()
            csvwriter.writerow(header)
            count += 1
        csvwriter.writerow(i.values())
    csv_data.close

# RUN FUNCTIONS
#Remove comments to run individual functions
#create teh sub accounts from the list above
#create_sub_account()
#propogate account settings from a specified account to all sub accounts
propogate_account_settings('me')
#propogate locked settings from a specified account to all sub accounts
propogate_locked_settings('me')
#propogate the groups from the specified account to all sub accounts
propogate_group_settings('me')


