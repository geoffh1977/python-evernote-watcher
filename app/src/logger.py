#!/usr/bin/env python2
import sys
import logging
import coloredlogs

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
coloredlogs.install(level=logging.INFO)
