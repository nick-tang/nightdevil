import socket, sys, select, SocketServer, struct, time, logging

BUFF_SIZE=16*1024

logging.basicConfig(level=logging.DEBUG)

class ThreadingTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

class Socks5Server(SocketServer.StreamRequestHandler):  
    def handle_tcp(self, sock, remote):  
        fdset = [sock, remote]  
        while True:  
            r, w, e = select.select(fdset, [], [])  
            if sock in r:  
                if remote.send(sock.recv(BUFF_SIZE)) <= 0:
                    for s in fdset:
                        s.close()
                    break  
            if remote in r:  
                if sock.send(remote.recv(BUFF_SIZE)) <= 0:
                    for s in fdset:
                        s.close()
                    break
    def handle(self):  
        try:  
            #print 'socks connection from ', self.client_address  
            sock = self.connection  
            # 1. Version  
            sock.recv(262)  
            sock.send(b"\x05\x00");  
            # 2. Request  
            data = self.rfile.read(4)  
            mode = ord(data[1])  
            addrtype = ord(data[3])  
            if addrtype == 1:       # IPv4  
                addr = socket.inet_ntoa(self.rfile.read(4))  
            elif addrtype == 3:     # Domain name  
                addr = self.rfile.read(ord(sock.recv(1)[0]))  
            port = struct.unpack('>H', self.rfile.read(2))  
            reply = b"\x05\x00\x00\x01"  
            try:  
                if mode == 1:  # 1. Tcp connect  
                    remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
                    remote.connect((addr, port[0]))  
                    #print 'Tcp connect to', addr, port[0]  
                else:  
                    reply = b"\x05\x07\x00\x01" # Command not supported  
                local = remote.getsockname()  
                reply += socket.inet_aton(local[0]) + struct.pack(">H", local[1])  
            except socket.error:  
                # Connection refused  
                reply = '\x05\x05\x00\x01\x00\x00\x00\x00\x00\x00'  
            sock.send(reply)  
            # 3. Transfering  
            if reply[1] == '\x00':  # Success  
                if mode == 1:    # 1. Tcp connect  
                    self.handle_tcp(sock, remote)  
        except socket.error:  
            pass #print 'socket error'
        except IndexError:
            pass
def sock5_run(host,port):  
    server=ThreadingTCPServer((host,port), Socks5Server)
    logging.info('Sock5 service listening at %s : %s'%(host,port))
    server.serve_forever()  
if __name__ == '__main__':
    HOST=''
    PORT=1081
    try:
        sock5_run(HOST,PORT)
    except KeyboardInterrupt:
        logging.info('Sock5 service stoped at %s : %s'%(HOST,PORT))
