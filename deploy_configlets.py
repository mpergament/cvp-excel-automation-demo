# Version 1.0: 07-08-2020, plavelle@arista.com
# Configlet builder to move devices to containers and apply configlets
# Do not attach directly to device/container - run this builder from the configlets page with no device selected

import requests
import json
from cvplibrary import CVPGlobalVariables, GlobalVariableNames

username = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_USERNAME)
password = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_PASSWORD)
cvp_url = 'https://localhost'
data_file = 'data.json'


def authenticate():
    url = cvp_url+'/web/login/authenticate.do'
    data = {'userId': username, 'password': password}
    return requests.post(url, data=json.dumps(data), verify=False)


def get_inventory():
    url = cvp_url+'/cvpservice/inventory/devices'
    cookies = authenticate().cookies
    response = requests.get(url, cookies=cookies, verify=False)
    return response.json()


def get_configlet(name):
    url = cvp_url+'/cvpservice/configlet/getConfigletByName.do?name=%s' % name
    cookies = authenticate().cookies
    response = requests.get(url, cookies=cookies, verify=False)
    return response.json()


def get_configlets_by_device_id(system_mac_address):
    url = cvp_url+'/cvpservice/provisioning/getConfigletsByNetElementId.do?netElementId=%s&startIndex=0&endIndex=0' % system_mac_address
    cookies = authenticate().cookies
    response = requests.get(url, cookies=cookies, verify=False)
    try:
        return response.json()['configletList']
    except:
        return None


def get_temp_configlets_by_device_id(system_mac_address):
    url = cvp_url+'/cvpservice/provisioning/getTempConfigsByNetElementId.do?netElementId=%s' % system_mac_address
    cookies = authenticate().cookies
    response = requests.get(url, cookies=cookies, verify=False)
    try:
        return response.json()['proposedConfiglets']
    except:
        return None


def get_container_key(parent_name):
    url = cvp_url+'/cvpservice/provisioning/searchTopology.do?queryParam=%s&startIndex=0&endIndex=0' % parent_name
    cookies = authenticate().cookies
    response = requests.get(url, cookies=cookies, verify=False)
    try:
        return response.json()['containerList'][0]['key']
    except:
        return None


def save_topology():
    url = cvp_url+'/cvpservice/provisioning/v2/saveTopology.do'
    cookies = authenticate().cookies
    requests.post(url, cookies=cookies, data=json.dumps([]), verify=False)


def move_device(device_dict, to_container_name):
    url = cvp_url+'/cvpservice/provisioning/addTempAction.do?format=topology&queryParam=&nodeId=root'
    cookies = authenticate().cookies
    msg = 'Moving device %s to container %s' % (device_dict['fqdn'], to_container_name)
    print(msg)
    to_container_key = get_container_key(to_container_name)
    data = {'data': [{'info': msg,
                      'infoPreview': msg,
                      'action': 'update',
                      'nodeType': 'netelement',
                      'nodeId': device_dict['systemMacAddress'],
                      'toId': to_container_key,
                      'fromId': device_dict['parentContainerKey'],
                      'nodeName': device_dict['fqdn'],
                      'fromName': '',
                      'toName': to_container_name,
                      'toIdType': 'container'}]}
    requests.post(url, cookies=cookies, data=json.dumps(data), verify=False)


def apply_configlets_to_device(device_dict, configlets, temp_configlets, name):
    url = cvp_url+'/cvpservice/provisioning/addTempAction.do?format=topology&queryParam=&nodeId=root'
    cookies = authenticate().cookies
    msg = 'Apply configlet %s to device %s' % (name, device_dict['fqdn'])
    print(msg)
    cnames = []
    ckeys = []
    for configlet in configlets:
        cnames.append(configlet['name'])
        ckeys.append(configlet['key'])
    for temp_configlet in temp_configlets:
        cnames.append(temp_configlet['name'])
        ckeys.append(temp_configlet['key'])
    key = get_configlet(name)['key']
    cnames.append(name)
    ckeys.append(key)
    data = {'data': [{'info': msg,
                      'infoPreview': msg,
                      'note': '',
                      'action': 'associate',
                      'nodeType': 'configlet',
                      'nodeId': '',
                      'configletList': ckeys,
                      'configletNamesList': cnames,
                      'ignoreConfigletNamesList': [],
                      'ignoreConfigletList': [],
                      'configletBuilderList': [],
                      'configletBuilderNamesList': [],
                      'ignoreConfigletBuilderList': [],
                      'ignoreConfigletBuilderNamesList': [],
                      'toId': device_dict['systemMacAddress'],
                      'toIdType': 'netelement',
                      'fromId': '',
                      'nodeName': '',
                      'fromName': '',
                      'toName': device_dict['fqdn'],
                      'nodeIpAddress': device_dict['ipAddress'],
                      'nodeTargetIpAddress': device_dict['ipAddress'],
                      'childTasks': [],
                      'parentTask': ''}]}
    requests.post(url, cookies=cookies, data=json.dumps(data), verify=False)


inventory = get_inventory()
database = json.loads(get_configlet(data_file)['config'])

for device in database:
    to_container_name = database[device]['device']['container']
    for item in inventory:
        if device == item['hostname']:
            move_device(item, to_container_name)

for device in database:
    for item in inventory:
        if device == item['hostname']:
            configlets = get_configlets_by_device_id(item['systemMacAddress'])
            temp_configlets = get_temp_configlets_by_device_id(item['systemMacAddress'])
            apply_configlets_to_device(item, configlets, temp_configlets, device)

save_topology()
