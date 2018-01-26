#!/usr/bin/env python

# (c) 2013, Greg Buehler
#
# This file is part of Ansible,
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

######################################################################

"""
Zabbix Server external inventory script.
========================================

Returns hosts and hostgroups from Zabbix Server.

Configuration is read from `zabbix.ini`.

Tested with Zabbix Server 2.0.6.
"""

from __future__ import print_function

import os, sys
import argparse

try:
        import configparser
except:
        from six.moves import configparser

try:
    from zabbix_api import ZabbixAPI
except:
    print("Error: Zabbix API library must be installed: pip install zabbix-api.",
          file=sys.stderr)
    sys.exit(1)

try:
    import json
except:
    import simplejson as json

class ZabbixInventory(object):

    def read_settings(self):
        config = configparser.SafeConfigParser()
        conf_path = './zabbix.ini'
        if not os.path.exists(conf_path):
	        conf_path = os.path.dirname(os.path.realpath(__file__)) + '/zabbix.ini'
        if os.path.exists(conf_path):
	        config.read(conf_path)
	else:
		self.zabbix_server = os.environ.get('ZABBIX_SERVER')
		self.zabbix_username = os.environ.get('ZABBIX_USERNAME')
		self.zabbix_password = os.environ.get('ZABBIX_PASSWORD')
		return

        # server
        if config.has_option('zabbix', 'server'):
            self.zabbix_server = config.get('zabbix', 'server')
	else:
	    self.zabbix_server = os.getenv('ZABBIX_SERVER','Error: server not provided.')

        # login
        if config.has_option('zabbix', 'username'):
            self.zabbix_username = config.get('zabbix', 'username')
	else:
	    self.zabbix_username =  os.getenv('ZABBIX_USERNAME','Error: username not provided.')

        if config.has_option('zabbix', 'password'):
            self.zabbix_password = config.get('zabbix', 'password')
	else:
	    self.zabbix_password = os.getenv('ZABBIX_USERNAME','Error: password not provided.')

    def read_cli(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--host')
        parser.add_argument('--list', action='store_true')
        self.options = parser.parse_args()

    def hoststub(self):
        return {
            'hosts': []
        }

    def get_host(self, api, name):
        data = {}
        return data

    def get_list(self, api):
        template_ids = None
        if os.getenv('ZABBIX_TEMPLATES'):
            template_ids = []
            templates = api.template.get({'output':'extend',
                'selectGroups':'extend', 
                'filter': {'host': os.getenv('ZABBIX_TEMPLATES').split(',')}})
            for template in templates:
                template_ids.append(template['templateid'])

        hostsData = api.host.get({'output': 'extend', 'selectGroups': 'extend', 'selectInterfaces': 'extend',
            'templateids': template_ids})

        data = {}
        data[self.defaultgroup] = self.hoststub()
        for host in hostsData:
            for interface in host['interfaces']:
                if interface['type'] == '1':
                    if interface['dns'] != '':
                        hostname = interface['dns']
                    else:
                        hostname = interface['ip']
                break
            data[self.defaultgroup]['hosts'].append(hostname)

            for group in host['groups']:
                groupname = group['name']

                if not groupname in data:
                    data[groupname] = self.hoststub()

                data[groupname]['hosts'].append(hostname)

        data['_meta'] = {'hostvars':{}}
        return data

    def __init__(self):

        self.defaultgroup = 'group_all'
        self.zabbix_server = None
        self.zabbix_username = None
        self.zabbix_password = None

        self.read_settings()
        self.read_cli()

        try:
            api = ZabbixAPI(server=self.zabbix_server)
            api.login(user=self.zabbix_username, password=self.zabbix_password)
        except BaseException as e:
            print("Error: Could not login to Zabbix server. Check your configuration.", file=sys.stderr)
            sys.exit(1)

        if self.options.host:
            data = self.get_host(api, self.options.host)
            print(json.dumps(data, indent=2))

        elif self.options.list:
            data = self.get_list(api)
            print(json.dumps(data, indent=2))

        else:
            print("usage: --list  ..OR.. --host <hostname>", file=sys.stderr)
            sys.exit(1)

ZabbixInventory()
