#!/usr/bin/python

import socket
import os

## This condition is perhaps fragile but works for Python 2.7.12 -- 3.5.2 at least:
#if socket.gethostbyname.__module__ == '_socket':
#    real_gethostbyname = socket.gethostbyname
#    def my_gethostbyname(hostname):
#        if hostname == os.environ.get('HOSTNAME', ''):
#            return '0.0.0.0'
#        return real_gethostbyname(hostname)
#    socket.gethostbyname = my_gethostbyname

from pysnmp.entity.rfc3413.oneliner import cmdgen # import is very slow
import logging

OID_AIRCARD_DRC_BUFFER = '1.3.6.1.3.234.15.1.0'
AIRCARD1 = 0
AIRCARD2 = 1

DRC_TO_KBPS = {
    0 : 0.0,
    1 : 38.4,
    2 : 76.8,
    3 : 153.6,
    4 : 307.2,
    5 : 307.2,
    6 : 614.4,
    7 : 614.4,
    8 : 921.6,
    9 : 1228.8,
    10: 1228.8,
    11: 1843.2,
    12: 2457.6,
    13: 1536.0,
    14: 3072.0,
    16: 460.8,
    17: 614.4,
    18: 768.0,
    19: 921.6,
    20: 1075.2,
    21: 1228.8,
    22: 1843.2,
    23: 2150.4,
    24: 2457.6,
    25: 3686.4,
    26: 4300.8,
    27: 4915.2
}

class PathExtract(object):
    def __init__(self, aircard):
        self.aircard_ip = '192.168.2.2' if aircard == AIRCARD1 else '192.168.3.2'
        self.auth_data = cmdgen.CommunityData('20071102')
        self.snmp_target = cmdgen.UdpTransportTarget((self.aircard_ip, 161))
        self.snmp_cmdgen = cmdgen.CommandGenerator()
        self.logger = logging.getLogger()

    def get_drc_snmp(self):
        avg_chan_bitrate = 0.
        n = 0.
        errorIndication, errorStatus, errorIndex, varBinds = self.snmp_cmdgen.getCmd(
            self.auth_data,
            self.snmp_target,
            OID_AIRCARD_DRC_BUFFER)

        if errorIndication:
            print(errorIndication)
        else:
            if errorStatus:
                self.logger.error('%s at %s', errorStatus.prettyPrint(),
                    errorIndex and varBindTable[-1][int(errorIndex)-1] or '?')
            else:
                if len(varBinds) == 1:
                    val = str(varBinds[0][1]) # first item returned, value
                    for xb in val:
                        x = ord(xb)
                        if x in DRC_TO_KBPS:
                            n += 1.
                            avg_chan_bitrate += (DRC_TO_KBPS[x] - avg_chan_bitrate) / n
                        else:
                            self.logging.warning("Unknown DRC index %d", x)
                else:
                    self.logger.warn("Wrong number of SNMP values") # preposterous!
        return avg_chan_bitrate

if __name__ == '__main__':
    pe = PathExtract(0)
    pe.get_drc_snmp()
