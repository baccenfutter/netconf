#!/usr/bin/env  python2
# -*- codi-ng: utf-8 -*-
__author__ = 'Brian Wiborg <baccenfutter@c-base.org>'
__license__ = 'public domain'
__date__ = '2013-12-27'

import logging
import commands

KILLALL = ['dhcpcd', 'dhclient', 'wvdial', 'wpa_supplicant']
logger = logging.getLogger('utils')


def get_available_interfaces():
    fd = open('/proc/net/dev', 'r')
    lines = fd.readlines()
    fd.close()
    return [l.split()[0][:-1] for l in lines[2:]]

def reset_interfaces():
    logger.info('resetting all interfaces...')
    ifaces = [i for i in get_available_interfaces()
              if i.startswith('eth') or i.startswith('wlan')]
    for iface in ifaces:
        status, output = commands.getstatusoutput(
            'ip addr flush dev %s' % iface
        )
        if status:
            print output
    for iface in ifaces:
        status, output = commands.getstatusoutput(
            'ip link set %s down' % iface
        )

def reset_daemons():
    logger.info('killing all daemons...')
    for daemon in KILLALL:
        output = commands.getoutput('killall -9 %s' % daemon)

def reset():
    reset_daemons()
    reset_interfaces()
