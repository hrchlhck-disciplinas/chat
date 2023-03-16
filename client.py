#!/usr/bin/env python3

import socket
import pickle
import os
import struct

from screen import Screen
from threading import Thread

USERNAME = ""

MULTICAST_GROUP = str(os.environ['MULTICAST_GROUP'])
MULTICAST_PORT = int(os.environ['MULTICAST_PORT'])

SERVER_IP = str(os.environ['SERVER_IP'])
SERVER_PORT = int(os.environ['SERVER_PORT'])

AUTHENTICATE = str(os.environ['AUTHENTICATE'])

def tratar_msg_recebida(addr: tuple, s: Screen):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sockfd:
        sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sockfd.bind(addr)
        mreq = struct.pack("4sl", socket.inet_aton(addr[0]), socket.INADDR_ANY)

        sockfd.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while True:
            data, _ = sockfd.recvfrom(1024)

            if not data:
                break

            data = pickle.loads(data)

            s.set_text(data['data'])

def autenticar(server: socket.socket, screen: Screen) -> bool:
    global USERNAME
    msg = server.recv(256).decode()
    screen.set_text(msg)
    uname = s.get_text()
    s._n_lines -= 1
    s.set_text(uname, col=len(msg))
    server.send(uname[:-1].encode('utf8'))

    USERNAME = uname

    if AUTHENTICATE == "yes":
        msg = server.recv(256).decode()
        s.set_text(msg)

        passwd = s.get_text()
        s._n_lines -= 1
        server.send(passwd[:-1].encode('utf8')) 
    
    confirm = server.recv(32).decode()

    if confirm != "OK\x01":
        s.set_text("Senha usuário ou senha inválidos")
        return False

    return True


if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sockfd:
        sockfd.connect((SERVER_IP, SERVER_PORT))
        
        with Screen() as s:
            t = Thread(target=tratar_msg_recebida, args=((MULTICAST_GROUP, MULTICAST_PORT), s))
            t.daemon = True
            t.start()

            is_authenticated = autenticar(sockfd, s)

            if not is_authenticated:
                sockfd.send("exit\x01".encode('utf8'))
                s.clear()
                exit(1)

            users_online = sockfd.recv(1).decode()
            s.set_text(f'Users connected: {users_online}')

            while True:
                try:
                    msg = s.get_text()
                    sockfd.send(msg.encode('utf8'))
                except KeyboardInterrupt:
                    sockfd.send("exit\x01".encode('utf8'))
                    s.clear()
                    break