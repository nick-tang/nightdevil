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

import json
import logging
import tcprelay


class nightdevil(object):
    
    def __init__(self,is_local,args=[]):

        self.is_local=is_local
        self.args=args
        
    def forever(self,config):
        
        server=tcprelay.TCPHandle(config,self.is_local)
        server.run()

    def print_info(self,data):
        logging.info(data)

    def load(self,conf):
        '''It always report error when the OS is windows,
        so I use eval() firstly instead just json.load(f)'''
        with open(conf) as f:
            data=json.dumps(eval(f.read()))
            return json.loads(data)

    def getconfig(self):
        if '-c' in self.args:
            try:
                config_path=self.args[self.args.index('-c')+1]
            except IndexError:
                print 'Config file path cannot be blank'
            config=self.load(config_path)
            return config
        elif '-h' in self.args:
            self.print_help()
            return
        elif '--help' in self.args:
            self.print_help()
            return
        else:
            return

    def print_help(self):
        print '''
Usage: python [server.py or local.py] [config file]...
# A fast tunnel proxy that helps you bypass firewalls.

Minier than shadowsocks & GFW.Press ,not only sock5 server
but also any service you want including HTTP Proxy ,etc

Only package is Pycrypto. It's a powerful secure tcp tunnel

Available Crypto Method:
    aes-128-cfb
    aes-192-cfb
    aes-256-cfb
    bf-cfb
    cast-cfb
    des3-cfb
    rc2-cfb
    chacha20
    salsa20

Proxy options:
    -c CONFIG              path to config file
    -h, --help             show this help message
    -d (invalid)           daemon mode (use nohup [linux])
                           or .vbs in windows like:
    <CreateObject("WScript.Shell").Run "[script]",0>
    
   
Online help: <https://github.com/Jason-Lyu/nightdevil>
'''





