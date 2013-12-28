#!/usr/bin/env  python2
# -*- coding: utf-8 -*
__author__ = 'Brian Wiborg <baccenfutter@c-base.org>'
__license__ = 'public domain'
__date__ = '2013-12-27'


class NetconfException(Exception):
    pass

class UnknownInterface(NetconfException):
    def __init__(self, message):
        self.message = "Unknown interface: %s" % message

class UnknownDhcpProvider(NetconfException):
    def __init__(self, message):
        self.message = "Unknown DHCP-Provider: %s" % message
