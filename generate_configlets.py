# Version 3.0: 06-08-2020, plavelle@arista.com
# Configlet builder to generate device configlets
# Do not attach directly to device/container - run this builder from the configlets page with no device selected

import requests
import json
from jinja2 import Template
from cvplibrary import CVPGlobalVariables, GlobalVariableNames

username = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_USERNAME)
password = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_PASSWORD)
cvp_url = 'https://localhost'
data_file = 'data.json'
template_file = 'infrastructure.j2'


def authenticate():
    url = cvp_url+'/web/login/authenticate.do'
    data = {'userId': username, 'password': password}
    return requests.post(url, data=json.dumps(data), verify=False)


def get_configlet(name):
    url = cvp_url+'/cvpservice/configlet/getConfigletByName.do?name=%s' % name
    cookies = authenticate().cookies
    response = requests.get(url, cookies=cookies, verify=False)
    return response.json()


def update_configlet(name, config):
    url = cvp_url+'/cvpservice/configlet/getConfigletByName.do?name=%s' % name
    cookies = authenticate().cookies
    response = requests.get(url, cookies=cookies, verify=False)
    response = response.json()
    if 'config' and 'key' in response:
        current_config = response['config']
        key = response['key']
        if current_config == config:
            pass
        else:
            print('Updating configlet ' + name)
            url = cvp_url+'/cvpservice/configlet/updateConfiglet.do'
            cookies = authenticate().cookies
            data = {'config': config, 'key': key, 'name': name, 'waitForTaskIds': True}
            requests.post(url, cookies=cookies, data=json.dumps(data), verify=False)
    else:
        print('Adding configlet ' + name)
        url = cvp_url+'/cvpservice/configlet/addConfiglet.do'
        cookies = authenticate().cookies
        data = {'config': config, 'name': name}
        requests.post(url, cookies=cookies, data=json.dumps(data), verify=False)


database = json.loads(get_configlet(data_file)['config'])
template = Template(get_configlet(template_file)['config'])

for device in database:
    device_database = database[device]
    config = 'hostname ' + device + '\n' + template.render(device_database)
    update_configlet(device, config)
