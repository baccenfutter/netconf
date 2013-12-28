#!/usr/bin/env  python2
# -*- coding: utf-8 -*-

import logging

import providers
import scanners
from utils import reset_interfaces, reset_daemons, reset

def get_debug_log_conf(filename=None):
    return {
        'filename': filename,
        'level': logging.DEBUG,
        'format': "%(asctime)s %(name)-12s %(levelname)-10s %(message)s"
    }

def get_default_log_conf(filename=None):
    return {
        'filename': filename,
        'level': logging.INFO,
        'format': '%(name)-10s %(message)s'
    }

logging.basicConfig(**get_default_log_conf(None))
