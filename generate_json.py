#!/usr/bin/env python3
# Version 0.3: 2020-03-08, plavelle@arista.com

import argparse
import json
import pandas as pd


def main():

    parser = argparse.ArgumentParser(
        description='Generate JSON from XLSX'
        )
    parser.add_argument(
        '-f',
        help='Input Excel file',
        dest='file',
        required=True
        )

    args = parser.parse_args()

    input_file = args.file
    sheets = ['device', 'interface', 'bgp']
    output_file = 'data.json'
    sheet_dict = {}

    def make_dict(input_file, sheet_name):
        df = pd.read_excel(input_file, sheet_name=sheet_name, dtype=str)
        for hostname in df.groupby('hostname').groups.keys():
            sheet_data = df.loc[df['hostname'] == hostname].drop('hostname', axis=1).to_dict(orient='records')
            sheet_data = [{k: v for k, v in x.items() if v == v} for x in sheet_data]
            if sheet_name == 'device':
                sheet_dict[hostname] = {}
                sheet_data = sheet_data[0]
                if 'container' in sheet_data:
                    container = sheet_data['container']
                    df_vlan = pd.read_excel(input_file, sheet_name='vlan', dtype=str)
                    vlan_data = df_vlan.loc[df_vlan['container'] == container].drop('container', axis=1).to_dict(orient='records')
                    vlan_data = [{k: v for k, v in x.items() if v == v} for x in vlan_data]
                    if len(vlan_data) != 0:
                        sheet_dict[hostname]['vlan'] = vlan_data
                    df_vrf = pd.read_excel(input_file, sheet_name='vrf', dtype=str)
                    vrf_data = df_vrf.loc[df_vrf['container'] == container].drop('container', axis=1).to_dict(orient='records')
                    vrf_data = [{k: v for k, v in x.items() if v == v} for x in vrf_data]
                    if len(vrf_data) != 0:
                        sheet_dict[hostname]['vrf'] = vrf_data
            sheet_dict[hostname][sheet_name] = sheet_data
        return sheet_dict


    for sheet_name in sheets:
        sheet_dict = make_dict(input_file, sheet_name)

    with open(output_file, 'w') as file:
        json.dump(sheet_dict, file, indent=4)

    print('Saved file: '+output_file)

if __name__ == "__main__":
    main()
