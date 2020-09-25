# Version 1.0: 06-08-2020, plavelle@arista.com
# Configlet builder to add containers
# Do not attach directly to device/container - run this builder from the configlets page with no device selected

import requests
import json
from cvplibrary import CVPGlobalVariables, GlobalVariableNames

username = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_USERNAME)
password = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_PASSWORD)
cvp_url = 'https://localhost'

containers = [
    {'Tenant': 'dc1'},
    {'dc1': 'dc1_spine'},
    {'dc1': 'dc1_leaf'}]


def authenticate():
    url = cvp_url+'/web/login/authenticate.do'
    data = {'userId': username, 'password': password}
    return requests.post(url, data=json.dumps(data), verify=False)


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


def add_container(parent_name, container_name):
    url = cvp_url+'/cvpservice/provisioning/addTempAction.do?format=topology&queryParam=&nodeId=root'
    cookies = authenticate().cookies
    msg = ('Adding container %s under container %s' %
           (container_name, parent_name))
    print(msg)
    parent_key = get_container_key(parent_name)
    data = {'data': [{'info': msg,
                      'infoPreview': msg,
                      'action': 'add',
                      'nodeType': 'container',
                      'nodeId': 'new_container',
                      'toId': parent_key,
                      'fromId': '',
                      'nodeName': container_name,
                      'fromName': '',
                      'toName': parent_name,
                      'toIdType': 'container'}]}
    requests.post(url, cookies=cookies, data=json.dumps(data), verify=False)
    save_topology()


for item in containers:
    for parent_name, container_name in item.items():
        add_container(parent_name, container_name)
