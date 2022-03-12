#!/usr/bin/python3

import socket
import threading

class Server:
    def __init__(self):
            self.ip = socket.gethostbyname(socket.gethostname())
            while 1:
                try:
                    self.port = 61616
                    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.s.bind((self.ip, self.port))

                    break
                except:
                    print("Couldn't bind to that port")

            self.connections = []
            self.accept_connections()

    def accept_connections(self):
        self.s.listen(100)

        print('Running on IP: '+self.ip)
        print('Running on port: '+str(self.port))
        
        while True:
            c, addr = self.s.accept()
            print(c, " Connected")

            self.connections.append(c)

            threading.Thread(target=self.handle_client,args=(c,addr,)).start()
        
    def broadcast(self, sock, data):
        for client in self.connections:
            if client != self.s and client != sock:
                try:
                    client.send(data)
                except:
                    pass

    def handle_client(self,c:socket.socket,addr):
        while 1:
            try:
                data = c.recv(512)
                self.broadcast(c, data)
            except socket.error:
                print(c, ' Disconnected')
                self.connections.remove(c)
                c.close()
                break
            
if __name__ == '__main__':
    server = Server()
