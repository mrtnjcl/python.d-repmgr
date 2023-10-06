
# Description: repmgrd monitoring netdata python.d module
# Author: mrtnjcl
# SPDX-License-Identifier: GPL-3.0-or-later

from random import SystemRandom
import subprocess

from bases.FrameworkServices.SimpleService import SimpleService


#node_id, node_name,     node_type, server running(0/1),repmgrd running (0/1/-1),PID,   Paused?(0/1/-1),priority, last seen     
#1,       node01,        standby,   1,                  0,                       -1,    0,              100,     -1,    default
#2,       node02,        primary,   1,                  1,                       244100,0,              100,     -1,    default
priority = 90000

ORDER = [
    'repmgrd_status',
    'repmgrd_paused',
    'server_status',
    'node_type'
]

CHARTS = {
    'repmgrd_status': {
        'options': [None, 'Repmgrd Daemon Status', 'running', 'repmgrd', 'repmgr.repmgrd_status', 'line'],
        'lines': [] 
    },
    'repmgrd_paused': {
        'options': [None, 'Repmgrd Daemon Run Info', 'paused', 'repmgrd', 'repmgr.repmgrd_paused', 'line'],
        'lines': [] 
    },
    'server_status': {
        'options': [None, 'Postgresql Server Status', 'running', 'psql', 'repmgr.server_status', 'line'],
        'lines': []
    },
    'node_type': {
        'options': [None, 'Postgresql Node Type (0=primary)', 'primary', 'psql', 'repmgr.node_type', 'line'],
        'lines': []
    }
}


class Service(SimpleService):
    def __init__(self, configuration=None, name=None):
        SimpleService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = CHARTS

    @staticmethod
    def check():
        return True

    def get_dim(self, node, chart, dimension):
        dim_id = ''.join([node, '_', chart, '_', dimension])
        if dim_id not in self.charts[chart]:
            self.charts[chart].add_dimension([dim_id, node, 'absolute', 1,1]) 
        return dim_id

    def get_data(self):
        data = dict()
        output = subprocess.check_output(['repmgr', 'daemon', 'status', '--csv'])
        for line in output.decode().splitlines():
            fields = line.split(',')
            node_name = fields[1]
            
            dimension_status = self.get_dim(node_name, 'repmgrd_status', 'status')
            dimension_paused = self.get_dim(node_name, 'repmgrd_paused', 'paused')
            dimension_server = self.get_dim(node_name, 'server_status', 'status')
            dimension_node_type = self.get_dim(node_name, 'node_type', 'node_type')

            data[dimension_status] = fields[4]
            data[dimension_paused] = fields[6]
            data[dimension_server] = fields[3]
            data[dimension_node_type] = 0 if fields[2] == 'primary' else 1	
        return data
