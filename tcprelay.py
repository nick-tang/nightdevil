# -*- coding: UTF-8 -*-
#
# Copyright (c) 2016-2017 Jason Lyu
#
# secure TCP tunnel with Sock5
#
# from TCPHandle
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


import os
import socket
import threading
import random
import select
import logging

from Cryptor.Encrypt import Cipher

__all__=['TCPHandle']

logging.basicConfig(level=logging.DEBUG)

BUFFSIZE=8*1024

class UnknownSocks(Exception):pass

class Sock5Error(Exception):pass

class SockProxyError(Exception):pass

class TCPHandle(object):
    
    def __init__(self,config,IS_LOCAL=True):
        
        self._is_local=IS_LOCAL

        self.LOCAL_HOST=config['local_host']
        self.LOCAL_PORT=config['local_port']

        self._KEY=config['password']
        self._METHOD=config['method']

        self.cipher=Cipher(self._KEY,self._METHOD)
        self.IV_LENGTH=self.cipher.get_iv_length()

        if 'sock5' in config and config['sock5']:
            self._sock5=True
            if self._is_local:
                self.TARGET_HOST=config['target_host']
                self.TARGET_PORT=config['target_port']
        else:
            self._sock5=False
            self.TARGET_HOST=config['target_host']
            self.TARGET_PORT=config['target_port']

        if 'md5_hash_auth' in config and config['md5_hash_auth']:
            self._mha=True
        else:
            self._mha=False

    def _eventloop(self,cs,ss,wait_to_read):
        cs_addr=cs.getpeername()
        ss_addr=ss.getpeername()
        if self._is_local:
            temp=cs;cs=ss;ss=temp
        socks=[cs,ss]
        while True:
            try:
                r, w, e = select.select(socks,[],[])
                for s in r:
                    if s is ss:
                        try:
                            recv=ss.recv(BUFFSIZE)
                        except socket.error:
                            raise SockProxyError('Remote closed: %s:%d'%ss_addr)
                        data=self._upstream_handle(recv)
                        if not data:
                            for sock in socks:
                                sock.close()
                            return
                        else:
                            try:
                                cs.sendall(data)
                            except socket.error:
                                raise SockProxyError('Client closed: %s:%d'%cs_addr)
                        
                    elif s is cs:
                        try:
                            recv=cs.recv(BUFFSIZE)
                        except socket.error:
                            raise SockProxyError('Client closed: %s:%d'%cs_addr)
                        data,wait_to_read,status=\
                        self._downstream_handle(recv,wait_to_read)
                        if data:
                            try:
                                ss.sendall(data)
                            except socket.error:
                                raise SockProxyError('Remote closed: %s:%d'%ss_addr)
                        if not status:
                            for sock in socks:
                                sock.close()
                            return
                        
            except Exception,e:
                logging.error('Event Error:%s'%e)
                for sock in socks:
                    sock.close()
                return

    def _formatlen(self,data):
        return str(data).rjust(8)

    def _portforward(self,cs):
        wait_to_read=''
        ss=self._create_remote_socket(self.TARGET_HOST,self.TARGET_PORT)
        if ss:
            self._eventloop(cs,ss,wait_to_read)
            return
        else:
            logging.error('Connect to %s:%d error'%
                          (self.TARGET_HOST,self.TARGET_PORT))
            cs.close()
            return

    def _create_remote_socket(self,host,port):
        try:
            addrs=socket.getaddrinfo(host,port,0,socket.SOCK_STREAM,
                                     socket.SOL_TCP)
            if len(addrs) <= 0:
                return False
            af,socktype,proto,canonname,addr=addrs[0]
            ss=socket.socket(af,socktype,proto)
            #ss.setsockopt(socket.SOL_TCP,socket.TCP_NODELAY,1)
            ss.connect(addr)
            return ss
        except socket.error:
            return False

    def _upstream_handle(self,recv):
        data=recv
        if len(recv) > 0:
            if self._mha:
                mhash=self.cipher.md5(data)
            else:
                mhash=os.urandom(32)
            if len(recv) < 2048:
                rand=random.randint(0,4096)
                noise=os.urandom(rand)
            else:
                rand=0
                noise=''
            data=self.cipher.encrypt(data)
            DLEN=self._formatlen(len(data+noise))
            NLEN=self._formatlen(rand)
            header=self.cipher.encrypt(DLEN+NLEN+mhash)
            data=header+data+noise
            return data
        else:
            return False

    def _downstream_handle(self,recv,wait_to_read):
        data=wait_to_read+recv
        if len(data) > 0:
            if len(data) <= (self.IV_LENGTH+8+8+32):
                wait_to_read=data;data=''
            else:
                header=self.cipher.decrypt(data[:self.IV_LENGTH+8+8+32])
                try:
                    DLEN=int(header[:8])
                    NLEN=int(header[8:16])
                    mhash=header[16:48]
                except:
                    raise UnknownSocks('Unknown socket come from')
                if len(data[(self.IV_LENGTH+8+8+32):]) < DLEN:
                    wait_to_read=data;data=''
                else:
                    wait_to_read=data[(self.IV_LENGTH+8+8+32+DLEN):]
                    data=data[(self.IV_LENGTH+8+8+32):(self.IV_LENGTH+8+8+32+DLEN-NLEN)]
                    data=self.cipher.decrypt(data)
                    if self._mha:
                        if mhash != self.cipher.md5(data):
                            raise UnknownSocks('md5 hash not match from')
            if not len(recv) <= 0:
                return data,wait_to_read,True
            else:
                return data,wait_to_read,False
        else:
            return data,wait_to_read,False

    def _sock5_handle(self,cs):
        wait_to_read=''
        try:
            cs.recv(BUFFSIZE)
            cs.send('\x05\x00')
            recv=cs.recv(BUFFSIZE)
            mode=ord(recv[1:2])
            addrtype=ord(recv[3:4])
            if mode==0x01:
                addrlength=ord(recv[4:5])
                target_host=recv[5:5+addrlength]
                target_port=256*ord(recv[5+addrlength:5+addrlength+1])\
                             +ord(recv[1+5+addrlength:5+addrlength+2])
                if addrtype==3:pass
                    #target_host=socket.gethostbyname(target_host)
                elif addrtype==1:
                    if not recv.count('.')==4:
                        target_host=recv[4:8]
                        target_hostr=''
                        for i in target_host:
                            target_hostr +=str(ord(i))+'.'
                        target_host=target_hostr[:-1]
                        target_port=256*ord(recv[4+4:4+4+1])+\
                                     ord(recv[4+4+1:4+4+2])
                else:
                    raise Sock5Error('IPV6 is not support')
                ss=self._create_remote_socket(self.TARGET_HOST,self.TARGET_PORT)
                if ss:
                    addrinfo=target_host+':'+str(target_port)
                    addrinfo=self._upstream_handle(addrinfo)
                    ss.sendall(addrinfo)
                else:
                    raise Sock5Error('Cannot connect remote server')
                cs.send('\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00')
                self._eventloop(cs,ss,wait_to_read)
            else :
                raise Sock5Error('Unknown command:%s'%mode)
        except Exception,e:
            logging.error('Sock5 server error:%s'%e)
            cs.close()
            #import traceback;traceback.print_exc()

    def _sock5_header(self,cs):
        wait_to_read=''
        while True:
            try:
                recv=cs.recv(BUFFSIZE)
                data,wait_to_read,status=self._downstream_handle(recv,wait_to_read)
                if data:
                    addr=data.split(':')
                    target_host=addr[0]
                    target_port=int(addr[1])
                    ss=self._create_remote_socket(target_host,target_port)
                    if ss:
                        self._eventloop(cs,ss,wait_to_read)
                        return
                    else:
                        logging.error('Connect to %s:%d error'%
                                      (target_host,target_port))
                        return
                if not status:
                    cs.close()
                    return
            except Exception,e:
                logging.error('Sock5 header error:%s'%e)
                cs.close()
                return
        
    def run(self):
        server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.LOCAL_HOST,self.LOCAL_PORT))
        if self._is_local and self._sock5:
            logging.info('Start Nightdevil Sock5 client at %s : %s'%
                         (self.LOCAL_HOST,self.LOCAL_PORT))
            handle=self._sock5_handle
        elif (not self._is_local) and self._sock5:
            logging.info('Start Nightdevil Sock5 server at %s : %s'%
                         (self.LOCAL_HOST,self.LOCAL_PORT))
            handle=self._sock5_header
        else:
            handle=self._portforward
            if not self._is_local:
                logging.info('Start Nightdevil server at %s : %s'%
                             (self.LOCAL_HOST,self.LOCAL_PORT))
            elif self._is_local:
                logging.info('Start Nightdevil client at %s : %s'%
                             (self.LOCAL_HOST,self.LOCAL_PORT))
        if self._mha:
            logging.info('MD5-Hash-Authentication with %s mode is enabled'%self._METHOD)
        server.listen(500)
        while True:
            conn,address=server.accept()
            task=threading.Thread(target=handle,args=(conn,))
            task.setDaemon(True)
            task.start()
            

