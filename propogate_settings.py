import requests
import jwt
import json
from datetime import datetime, timedelta
import csv
import string
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
API_KEY = "YOUR API KEY HERE"
API_SECRET = "YOUR API SECRET HERE"
JWT_EXPIRY = 60
BASE_URL = 'https://api.zoom.us/v2/'

#List of groups and roles that will not be replicated to sub accounts
# list each group and role  name here
DO_NOT_REPLICATE = ['groupname1','groupname2','groupname3']
DO_NOT_REPLICATE_ROLE ['rolename1','rolename2','rolename3']

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

"""
Get JWT token, assemble headers, assemble endpoint URL, Log URL and Headers, send patch request with payload.
If status is not 200 log warning otherwise log response content as info
return response content
"""
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

"""
Get JWT token, assemble headers, assemble endpoint URL, Log URL and Headers, send post request with payload.
If status is not 200 log warning otherwise log response content as info
return response content
"""
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

 ##############################
 #     ACCOUNT FUNCTIONS      #
 ##############################

"""
Get a list of sub accounts and add each to a list
"""
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

"""
Get the account settings for a specific account and return them
"""
def get_account_settings(accountID):
    logging.info("Get Account Settings")
    url = '/accounts/%s/settings' % accountID
    #print(url)
    response = send_get_request(url)
    data = response
    encoded_data = json.loads(data)
    #print(encoded_data)
    return(encoded_data)

"""
Change the account settings of a specified account to the settings defined in the payload
"""
def update_account_settings(accountID, payload):
    logging.info("Update Account Settings: %s" % accountID)
    url = '/accounts/%s/settings' % accountID
    data = payload
    response = send_patch_request(url, json.dumps(data))
    print(response)
    return(response)

"""
get the locked settings from a specified account and return that data
"""
def get_locked_settings(accountID):
    logging.info("Get Locked Settings")
    url = "/accounts/%s/lock_settings" %accountID
    response = send_get_request(url)
    data = response
    encoded_data = json.loads(data)
    #print(encoded_data)
    return(encoded_data)

"""
Get a list of sub accounts for a specified account then get the settings from the specified account
for each account in the list of sub accounts apply the settings from the specified account
"""
def update_sub_accounts(fromAccount):
    logging.info("Update Sub Accounts")
    account_list = list_sub_accounts()
    account_settings = get_account_settings(fromAccount)
    for account in account_list:
        response = update_account_settings(account, account_settings)
        print(response)

"""
Get a list of sub accounts for a specified account then get the locked settings from the specified account
for each account in the list of sub accounts apply the locked settings from the specified account
"""
def update_locked_settings(accountID, payload):
    logging.info("Update Locked Settings: %s" % accountID)
    url = '/accounts/%s/settings' % accountID
    data = payload
    response = send_patch_request(url, json.dumps(data))
    print(response)
    return(response)

"""
get a list of sub accounts for a specified account, get a list of groups from the main account for each acccount in the sub account list create the groups as they are in the main account
"""
def update_sub_account_groups():
    logging.info("Update Sub Account Groups")
    account_list = list_sub_accounts()
    groups = list_groups('me')
    for account in account_list:
        for group in groups:
            response = create_group(account, group)
            print(response)

"""
get a list of sub accounts get the settings from a specified account for each account in sub account list update account settings to match the specified account
"""
def propogate_account_settings(fromAccount):
    logging.info("Propogate Account Settings")
    account_list = list_sub_accounts()
    payload = get_account_settings(fromAccount)
    for account in account_list:
        response = update_account_settings(account, payload)
        time.sleep(.300)
        print(response)

"""
get a list of sub accounts get the locked settings from a specified account for each account in sub account list update locked account settings to match the specified account
"""
def propogate_locked_settings(fromAccount):
    logging.info("Propogate Locked Settings")
    account_list = list_sub_accounts()
    payload = get_locked_settings(fromAccount)
    for account in account_list:
        response = update_locked_settings(account, payload)
        time.sleep(.300)
        print(response)

 ##############################
 #       GROUP FUNCTIONS      #
 ##############################

"""
function to create a group on a specified account with a specified group name
"""
def create_group(accountID, groupName):
    logging.info("Create Group")
    url = '/accounts/%s/groups' % accountID
    print(url)
    payload = {'name' : '%s' % groupName}
    response = send_post_request(url, json.dumps(payload))
    print(response)
    return(response)

"""
get a list of groups from a speciffied account and add the group id to a list and return that list
Need to modify to allow disabling of certain groups
"""
def list_groups(accountID):
    logging.info("List Groups")
    groups = []
    url = '/v2/accounts/%s/groups' % accountID
    response = send_get_request(url)
    print('response is : %s' % response)
    encoded_data=json.loads(response)
    for item in encoded_data['groups']:
        group = item['id']
        if group not in DO_NOT_REPLICATE:
            groups.append(group)
    return(groups)

"""
get settings from a specified group on a specified acount
"""
def get_group_settings(accountID, group):
    logging.info("Get Group Settings")
    url = '/accounts/%s/groups/%s/settings' % accountID, group
    response = send_get_request(url)
    return(response)

"""
update the settings of a specified group on a specified account with a specified payload
"""
def update_group_settings(accountID, group, payload):
    logging.info("Update Group Settings: %s : %s" % accountID, group)
    url = '/accounts/%s/groups/%s/settings' % accountID, group
    response = send_patch_request(url, json.dumps(payload))
    return(response)

"""
get a list of sub accounts, get a list of groups from a specified account, for eacch group in specified account get that groups settings.
for each account in sub account list update the settings of each group
"""
def propogate_group_settings(fromAccount):
    logging.info("Propogate Group Settings")
    account_list = list_sub_accounts()
    group_list = list_groups(fromAccount)
    for group in group_list:
        payload = get_group_settings(fromAccount, group)
        for account in account_list:
            response = update_group_settings(account, group, payload)
            time.sleep(.300)
            print(response)

 ##############################
 #       ROLE FUNCTIONS       #
 ##############################
 """
Role Propogation is untested
 """

"""
get a value from the response of list roles and add it to a list and return that list
"""
 def get_role_value(fromAccount, key):
    logging.info("Get Roles")
    values = []
    url = '/accounts/%s/roles/' % fromAccount
    response = send_get_request(url)
    encoded_data=json.loads(response)
    for item in encoded_data['roles']:
        value = item[key]
        if role not in DO_NOT_REPLICATE_ROLE:
            values.append(value)
    return(values)

"""
Get the settings of a particular role and return them
"""
def get_role_settings(fromAccount, roleID):
    logging.info("Get Role Settings")
    url = '/accounts/%s/roles/%s' % fromAccount, roleID
    response = send_get_request(url)
    return(response)

"""
Update the settings of a specific role
"""
def update_role_settings(accountID, roleID, payload):
    logging.info("update role settings")
    url = '/accounts/%s/roles/%s' % accountID, roleID
    payload = payload 
    response = send_patch_request(url, payload)
    return(response)

"""
Create a role
"""
def create_role(accountID, name):
    logging.info("Create Role")
    url = '/v2/accounts/%s/roles' % accountID
    payload = {"name" : "%s" % name} 
    reponse = send_post_request(url, payload)
    return(response)

"""
get a list of sub-accounts, get a list of roleID's, get a list of roleNames. for each role in the master account that is not on the exclusion list get that roles settings.
for each account in the sub-account list create the roles from the role_name_list and update its settings to match the corresponding role in the master account
"""
def propogate_roles(fromAccount):
    logging.info("Propogate Role Settings")
    account_list = list_sub_accounts()
    role_id_list = get_role_value(fromAccount, 'id')
    role_name_list = get_role_value(fromAccount, 'name')
    count = 0
    for roleID in role_id_list:
        payload = get_role_settings(fromAccount, roleID)
        for account in account_list:
            response =create_role(account, role_name_list[count])
            encoded_data=json.loads(response)
            for item in encoded_data['properties']:
                roleID = item['id']
            update_role_settings(account, roleID, payload)
            count +=1


        

##############################
#       RUN FUNCTIONS        #
##############################
"""
Comment out any function you do not wish to run
"""

#propogate account settings from a specified account to all sub accounts
propogate_account_settings('me')
#propogate locked settings from a specified account to all sub accounts
propogate_locked_settings('me')
#propogate the groups from the specified account to all sub accounts
propogate_group_settings('me')
#propogate the roles from the specified account to all sub-accounts
propogate_roles('me')