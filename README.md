# nightdevil
A fast secure tcp tunnel &amp; sock5 ,minier than shadowsocks or GFW.Press, but still powerful

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
