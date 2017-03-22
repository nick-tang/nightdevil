# -*- coding: UTF-8 -*-

import socket
import threading
import select
import logging

logging.basicConfig(level=logging.DEBUG)

BUFFSIZE=32*1024

class TransFormer:
    def __init__(self,LOCAL_HOST,LOCAL_PORT,TARGET_HOST,TARGET_PORT):
        self.LOCAL_HOST=LOCAL_HOST
        self.LOCAL_PORT=LOCAL_PORT
        self.TARGET_HOST=TARGET_HOST
        self.TARGET_PORT=TARGET_PORT

    def proxy(self,cs):
        try:
            ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            ss.connect((self.TARGET_HOST,self.TARGET_PORT))
        except:
            logging.error('Connect to remote server error')
            return
        socks=[cs,ss]
        caddr,cport=cs.getpeername()
        saddr,sport=ss.getpeername()
        while True:
            try:
                r, w, e = select.select(socks, [], [])
                for s in r:
                    if s is cs:
                        recv=cs.recv(BUFFSIZE)
                        if (len(recv) > 0):
                            logging.debug('%s : %s < %s > %s : %s'%(caddr,cport,len(recv),saddr,sport))
                            ss.sendall(recv)
                        else:
                            for sock in socks:
                                sock.close()
                            return
                    elif s is ss:
                        recv=ss.recv(BUFFSIZE)
                        if (len(recv) > 0):
                            #logging.debug('%s : %s < %s > %s : %s'%(saddr,sport,len(recv),caddr,cport))
                            cs.sendall(recv)
                        else:
                            for sock in socks:
                                sock.close()
                            return
            except Exception,e:
                logging.error('Proxy data error:%s'%e)
                for sock in socks:
                    sock.close()
                return
    def run(self):
        ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ls.bind((self.LOCAL_HOST,self.LOCAL_PORT))
        #print 'Start service at',self.LOCAL_HOST,':',self.LOCAL_PORT
        logging.info('Start service at %s : %s'%(self.LOCAL_HOST,self.LOCAL_PORT))
        ls.listen(100)
        while True:
            try:
                clientSock, address = ls.accept()
            except KeyboardInterrupt:
                ls.close()
                logging.warning('Stop port forward service') 
                break
            threading.Thread(target=self.proxy, args=(clientSock,)).start()

if __name__ == "__main__":
    LOCAL_HOST='172.20.7.4'
    LOCAL_PORT=5555

    TARGET_HOST='172.20.7.4'
    TARGET_PORT=8888

    server=TransFormer(LOCAL_HOST,LOCAL_PORT,TARGET_HOST,TARGET_PORT)
    server.run()

