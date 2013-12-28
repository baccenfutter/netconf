#!/usr/bin/env  python2
# -*- coding: utf-8 -*-
__author__ = 'Brian Wiborg <baccenfutter@c-base.org>'
__license__ = 'public domain'
__date__ = '2013-12-27'


import os
import logging
import commands
import utils
import exceptions
import ipaddr

from wifi import Cell

DHCP_PROVIDERS = {
    'dhcpcd': '/sbin/dhcpcd',
    'dhclient': '/sbin/dhclient',
}


class Iface(object):
    def __init__(self, name):
        self.logger = logging.getLogger('iface')
        self.logger.debug('initializing: %s' % name)
        if name not in utils.get_available_interfaces():
            raise exceptions.UnknownInterface(name)
        self.name = name
        self.logger.debug('utilizing: %s' % self.name)

    def __repr__(self):
        return self.name

    def is_wired(self):
        return self.name.startswith('eth')

    def is_wireless(self):
        return self.name.startswith('wlan')

    def is_virtual(self):
        return bool(not self.is_wired() and not self.is_wireless())

    def ifup(self):
        self.logger.info('ifup: %s' % self.name)
        status, output = commands.getstatusoutput(
            'ip link set %s up' % self.name
        )
        if status:
            self.logger.error(output)
            raise NetconfException(output)

    def ifdown(self):
        self.logger.info('ifdown: %s' % self.name)
        status, output = commands.getstatusoutput(
            'ip link set %s down' % self.name
        )
        if status:
            self.logger.error(output)
            raise NetconfException(output)

    def flush(self):
        self.logger.info('flushing addresses: %s' % self.name)
        status, output = commands.getstatusoutput(
            'ip addr flush dev %s' % self.name
        )
        if status:
            self.logger.error(output)
            raise NetconfException(output)

    def print_config(self):
        print commands.getoutput(
            'ip addr show %s | tail -n +3' % self.name
        )
        print
        print ' ' * 4 + commands.getoutput(
            'ip r | grep "^default"'
        )
        print
        output = commands.getoutput(
            'grep -v "^#" /etc/resolv.conf | grep -v "^$"'
        )
        for line in output.split('\n'):
            print ' ' * 4 + line


class Dhcp(object):
    def __init__(self, provider):
        self.logger = logging.getLogger('dhcp')
        self.logger.debug('inititalizing')
        if provider not in DHCP_PROVIDERS:
            raise exceptions.UnknownDhcp(provider)
        self.provider = DHCP_PROVIDERS[provider]
        self.logger.debug('utilizing: %s' % self.provider)

    def __call__(self, iface):
        if not isinstance(iface, Iface):
            raise ValueError(
                'must be of type: netconf.providers.Iface'
            )
        self.logger.info('requesting lease via %s' % self.provider)
        status, output = commands.getstatusoutput(
            '%s %s' % (self.provider, iface)
        )
        if status:
            self.logger.error(output)
            raise exceptions.NetconfException(output)


class Address(object):
    def __init__(self, cidr):
        self.logger = logging.getLogger('address')
        self.logger.debug('initializing...')
        self.address = ipaddr.IPNetwork(cidr)
        self.logger.debug('utilizing: %s' % self.address)

    def __call__(self, iface):
        if not isinstance(iface, Iface):
            raise ValueError(
                'Must be of type: netconf.providers.Iface'
            )
        iface.ifup()
        self.logger.info(
            'configuring: %s -> %s' % (self.address, iface)
        )
        status, output = commands.getstatusoutput(
            'ip a a %s dev %s' % (self.address.with_prefixlen, iface)
        )
        if status:
            self.logger.error(output)
            raise exceptions.NetconfException(output)


class Gateway(object):
    def __init__(self, gateway):
        self.logger = logging.getLogger('gateway')
        self.logger.debug('initializing...')
        self.gateway = ipaddr.IPAddress(gateway)
        self.logger.debug('utilizing: %s' % self.gateway)

    def __call__(self):
        self.logger.info('routing via: %s' % self.gateway)
        status, output = commands.getstatusoutput(
            'ip r a default via %s' % self.gateway
        )
        if status:
            self.logger.error(output)
            raise NetconfException(output)


class Resolver(object):
    def __init__(self, address, domain=None, search=None, clear=True):
        self.logger = logging.getLogger('resolver')
        self.logger.debug('initializing...')
        self.address = ipaddr.IPAddress(address)
        self.domain = domain
        self.search = search
        self.clear = clear

    def __call__(self):
        self.logger.info('resolving via: %s' % self.address)
        if self.clear:
            fd = open('/etc/resolv.conf', 'w')
            fd.write('nameserver %s\n' % self.address)
        else:
            fd = open('/etc/resolv.conf', 'a')
            fd.write('nameserver %s\n' % self.address)
        if self.domain:
            fd.write('domain %s\n' % self.domain)
        if self.search:
            fd.write('search %s\n' % self.search)
        fd.close()


class Wifi(object):
    def __init__(self, essid):
        self.logger = logging.getLogger('iwlist')
        self.logger.debug('initializing...')
        self.essid = essid

    def __call__(self, iface):
        if not isinstance(iface, Iface):
            raise ValueError(
                'must be of type: net_conf.providers.Iface'
            )
        if not iface.is_wireless():
            raise TypeError(
                'must be of type: wireless'
            )
        cell = Cell([])
        cell.essid = self.essid
        cell(iface)


class Wpa(object):
    def __init__(self, config, driver='wext'):
        self.logger = logging.getLogger('supplicant')
        self.logger.debug('initializing...')
        if not os.path.exists(config):
            raise IOError('Broken path: %s' % config)
        self.config = config
        self.driver = driver
        self.logger.debug('utilizing: %s' % self.config)

    def __call__(self, iface):
        if not isinstance(iface, Iface):
            raise ValueError(
                'must be of type: netconf.providers.Iface'
            )
        if not iface.is_wireless():
            raise TypeError('must be of type: wireless')
        iface.ifup()
        self.logger.info('connecting: %s' % self.config)
        status, output = commands.getstatusoutput(
            'wpa_supplicant -i %s -D %s -c %s -B' % (iface, self.driver,
                                                     self.config)
        )
        if status:
            self.logger.error(output)
            raise NetconfException(output)

