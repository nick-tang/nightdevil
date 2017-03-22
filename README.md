==== nightdevil
A fast secure tcp tunnel &amp; sock5 ,smaller than shadowsocks or GFW.Press, but still powerful


# Copyright (c) 2016-2017 Jason Lyu

# secure TCP tunnel with Sock5     
 
        
   AES-256-CFB header:      
	+-----+----+-------+--------+--------+--------------+-------------+           
	|&nbspIV1&nbsp|SIZE|&nbspNSIZE&nbsp|&nbsp&nbspHASH&nbsp&nbsp|&nbsp&nbspIV2&nbsp&nbsp&nbsp|&nbsp&nbsp&nbsp&nbsp&nbspDATA&nbsp&nbsp&nbsp&nbsp&nbsp|&nbspNOISE&nbspBYTES&nbsp|     
	+-----+----+-------+--------+--------+--------------+-------------+             
	|&nbsp16&nbsp&nbsp|&nbsp&nbsp8&nbsp|&nbsp&nbsp&nbsp8&nbsp&nbsp&nbsp|&nbsp&nbsp&nbsp32&nbsp&nbsp&nbsp|&nbsp&nbsp&nbsp16&nbsp&nbsp&nbsp|&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp1+&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp|&nbsp&nbsp&nbsp&nbsp&nbsp0+&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp|            
	+-----+----+-------+--------+--------+--------------+-------------+          

---- Writen by threading + select         

# There are two mode:               
(1)sock5 proxy with crypto <'sock5'=True>               
(2)portforward with	crypto <'sock5'=False>               

if the mode is sock5 proxy,it doesn't request 'target_host' or               
'target_port' options,so it would be ignored.               

if the mode is portforward,it requests 'target_host' and               
'target_port' options.               

You can open or close the md5-hash-auth,if you don't care about                
whether the data is reseted.               

Make sure your server has installed pycrypto module,and it has                
enough RAM to run this scripts,because it depends on threading               

The Crypto mode of chacha20 and salsa20 are pure python scripts,               
so it may not a best choise to encrypt data.               

#HELP:               

Usage: python [server.py or local.py] [config file]...               
 A fast tunnel proxy that helps you bypass firewalls.               

Smaller than shadowsocks & GFW.Press ,not only sock5 server               
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
