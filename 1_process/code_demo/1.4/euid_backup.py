#!/usr/bin/env python
# -*- coding: utf-8 -*
# Copyright: See LICENSE for details.
# Authors: Guannan Ma (@mythmgn),
"""
backup files
"""

from __future__ import print_function
import os
import time

print('euid is {0}'.format(os.geteuid()))

if os.geteuid() == 0:
    print('start to copy under root')
    time.sleep(2)
    print('end copying things')
    print('drop privileges from root')
else:
    print('non-root, euid {0} will exit'.format(os.geteuid()))

# vi:set tw=0 ts=4 sw=4 nowrap fdm=indent
