# -*- coding: UTF-8 -*-
#
# Copyright (c) 2016-2017 Jason Lyu
#
# secure TCP tunnel with Sock5
#
#
# Above all : make sure you have installed Pycrypto
#
#   AES-256-CFB:
#	+-----+----+-------+--------+--------+--------------+-------------+
#	| IV1 |SIZE| NSIZE |  HASH  |  IV2   |     DATA     | NOISE BYTES | 
#	+-----+----+-------+--------+--------+--------------+-------------+
#	| 16  |  8 |   8   |   32   |   16   |      1+      |     0+      | 
#	+-----+----+-------+--------+--------+--------------+-------------+
#

import sys
import traceback
from control import nightdevil

IS_LOCAL=False

CONFIG={
    'local_host':'127.0.0.1',
    'local_port':5555,
    'target_host':'127.0.0.1',
    'target_port':1081,
    'password':'password',
    'method':'aes-256-cfb',
    'md5_hash_auth':True,
    'sock5':True
    }


if __name__ == "__main__":
    args=sys.argv
    server=nightdevil(IS_LOCAL,args)
    if len(args) > 1:
        conf=server.getconfig()
    else:
        conf=CONFIG
    try:
        if conf:
            server.forever(conf)
    except KeyboardInterrupt:
        server.print_info('Stopping Nightdevil server ...')
        sys.exit()
    except Exception,e:
        traceback.print_exc()
        sys.exit()

