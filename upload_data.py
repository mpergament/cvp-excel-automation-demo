from cvprac.cvp_client import CvpClient
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

clnt = CvpClient()

clnt.connect(
    nodes=['34.90.178.133'],
    username='arista', password='arista', is_cvaas=False
)

with open('data.json') as json_file:
    data = json.load(json_file)
    taskInfo = clnt.api.add_configlet (
        name="data.json",
        config=json.dumps(data, indent=4)
    )

data=open("infrastructure.j2", 'r').read()
taskInfo = clnt.api.add_configlet (
    name="infrastructure.j2",
    config=data
)

builder_list = ["generate_configlets.py", "generate_json.py"]

for builder in builder_list:
    data=open(builder, 'r').read()
    taskInfo = clnt.api.add_configlet_builder (
        name=builder,
        config=data
    )