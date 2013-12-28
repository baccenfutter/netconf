#!/usr/bin/env  python2
# -*- coding: utf-8 -*-
__author__ = 'Brian Wiborg <baccenfutter@c-base.org>'
__license__ = 'public domain'
__date__ = '2013-12-27'

import re
import time
import logging
import commands
import exceptions
from providers import Iface
from wifi import Cell

CELL_START_MARK = re.compile(r'^Cell\s\d\d\s-\sAddress:.*')

class IwScan(object):
    def __init__(self):
        self.logger = logging.getLogger('iwscan')
        self.logger.debug('initializing...')
        self.cells = None
        self.__iface = None

    def __call__(self, iface=None):
        if iface is None:
            return '%s' % self
        else:
            if not isinstance(iface, Iface):
                raise ValueError(
                    'must be of type: net_conf.providers.Iface'
                )
            self.__iface = iface

            self.logger.info('scanning: %s' % iface)
            commands.getoutput('ip link set %s up' % iface)
            for i in range(3):
                status, output = commands.getstatusoutput(
                    'iwlist %s scan' % iface
                )
                if status:
                    self.logger.info('retrying...')
                    time.sleep(1)
                else:
                    break
            if status:
                self.logger.error(output)
                raise exceptions.NetconfException(output)

            cells = []
            cell_block = []
            for line in [l.strip() for l in output.split('\n')][1:]:
                if cell_block:
                    cell_start = CELL_START_MARK.match(line)
                    if not cell_start is None:
                        cells.append(Cell(cell_block))
                        cell_block = []
                cell_block.append(line)
            self.cells = cells

    def __repr__(self):
        output = ''
        if self.cells is None:
            self.logger.error('scanning will lead to better results...')
            return output
        for counter, cell in enumerate(self.cells):
            output += '%3s %s\n' % (counter + 1, cell)
        return output

    def selection(self):
        self.connect_to(
            int(raw_input('where would you like to go today? '))
        )

    def connect_to(self, num):
        if not self.__iface:
            return
        self.cells[num - 1](self.__iface)

