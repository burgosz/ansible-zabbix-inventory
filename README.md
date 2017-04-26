# ansible-zabbix-inventory
Ansible inventory script for Zabbix

This script is based on the offical Ansible Zabbix inventory script, extended with template filtering.
To use template filtering set ZABBIX_TEMPLATES environment variable to the list of template names seperated with comma. If ZABBIX_TEMPLATES is unset the script returns all hosts.

Before usage fill your credentials in zabbix.ini

Example:
```
ZABBIX_TEMPLATES='Template OS Linux,Template App Docker' ansible -i zabbix.py all -m ping
```
This will only add hosts with Template OS Linux or Template App Docker templates to the inventory.
