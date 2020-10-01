from cvprac.cvp_client import CvpClient
import json
import urllib3
import argparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser(
    description='Upload Configlets to CVP'
    )
parser.add_argument(
    '-i',
    help='CVP IP address',
    dest='ip',
    required=True
    )

args = parser.parse_args()

ip = args.ip

clnt = CvpClient()

clnt.connect(
    nodes=[ip],
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

builder_list = ["generate_configlets.py", "deploy_configlets.py", "add_containers.py"]

for builder in builder_list:
    data=open(builder, 'r').read()
    taskInfo = clnt.api.add_configlet_builder (
        name=builder,
        config=data
    )