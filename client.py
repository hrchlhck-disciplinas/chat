#!/usr/bin/env python3

import socket
import pickle
import struct
import os

from threading import Thread

USERNAME = ""

MULTICAST_GROUP = str(os.environ['MULTICAST_GROUP'])
MULTICAST_PORT = int(os.environ['MULTICAST_PORT'])

SERVER_IP = str(os.environ['SERVER_IP'])
SERVER_PORT = int(os.environ['SERVER_PORT'])

def tratar_input(addr: tuple):
    global USERNAME
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sockfd:
        sockfd.connect(addr)

        uname = sockfd.recv(256).decode()
        print(uname)

        msg = input(">>> ")
        sockfd.send(msg.encode('utf8'))

        confirm = sockfd.recv(128).decode()

        if confirm != "OK\x01":
            print(confirm)
            exit(1)

        users_online = sockfd.recv(1).decode()
        print('Users connected:', users_online)

        USERNAME = msg

        while True:
            try:
                msg = input(">>> ")
                sockfd.send(msg.encode('utf8'))
            except KeyboardInterrupt:
                sockfd.send("exit\x01".encode('utf8'))
                break

def tratar_msg_recebida(addr: tuple):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sockfd:
        sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sockfd.bind(addr)
        mreq = struct.pack("4sl", socket.inet_aton(addr[0]), socket.INADDR_ANY)

        sockfd.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while True:
            data, _ = sockfd.recvfrom(1024)

            data = pickle.loads(data)

            if data['sender'] != USERNAME:
                print(data['data'])

if __name__ == '__main__':
    print(SERVER_IP, SERVER_PORT)
    Thread(target=tratar_msg_recebida, args=((MULTICAST_GROUP, MULTICAST_PORT),)).start()
    tratar_input((SERVER_IP, SERVER_PORT))