#!/usr/bin/env  python2
# -*- coding: utf-8 -*-
__author__ = 'Brian Wiborg <baccenfutter@c-base.org>'
__license__ = 'public domain'
__date__ = '2013-12-27'

import logging
import commands
import exceptions

from tempfile import NamedTemporaryFile


TPL_UNENCRYPTED = """network={
    ssid="%s"
    key_mgmt=NONE
}"""


class Cell(object):
    def __init__(self, data):
        self.logger = logging.getLogger('cell')
        self.logger.debug('initializing...')
        data = [l for l in data if not l.startswith('IE: Unknown:')]
        self.address = ''
        self.essid = ''
        self.encryption = False
        self.ciphers = {
            'group': '',
            'pairwise': '',
        }
        self.bitrates = []
        for line in data:
            if line.startswith('Cell '):
                self.address = line.split()[-1]
            elif line.startswith('ESSID:"'):
                self.essid = line.split('"')[1]
            elif line.startswith('Bit Rates:'):
                self.bitrates.append(line.split(':')[1].strip())
            elif line.startswith('Encryption '):
                self.encryption = bool(line.split(':')[1] == 'on')
            elif line.startswith('Group Cipher :'):
                self.ciphers['group'] = line.split(':')[1].strip()
            elif line.startswith('Pairwise Ciphers '):
                self.ciphers['pairwise'] = line.split(':')[1].strip()

    def __repr__(self):
        return '%-24s [enc:%s][%s] Bitrates: %s' % (
            self.essid, self.encryption, self.address, self.bitrates
        )

    def __call__(self, iface, driver='wext'):
        from providers import Iface
        if not isinstance(iface, Iface):
            raise ValueError(
                'must be of type: net_conf.providers.Iface'
            )
        if not iface.is_wireless():
            raise TypeError('must be of type: wireless')
        iface.ifup()

        self.logger.info('connecting: %s' % self.essid)
        config = TPL_UNENCRYPTED % self.essid
        f = NamedTemporaryFile()
        f.file.write(config)
        f.file.flush()
        status, output = commands.getstatusoutput(
            'wpa_supplicant -i %s -D %s -c %s -B' % (iface, driver,
                                                     f.name)
        )
        if status:
            self.logger.error(output)
            raise exceptions.NetconfException(output)

