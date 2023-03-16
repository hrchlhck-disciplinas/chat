#!/usr/bin/env python3

import socket
import pickle
import os

from datetime import datetime as dt
from threading import Thread

connected_users = list()

MULTICAST_GROUP = str(os.environ['MULTICAST_GROUP'])
MULTICAST_PORT = int(os.environ['MULTICAST_PORT'])

SERVER_IP = str(os.environ['SERVER_IP'])
SERVER_PORT = int(os.environ['SERVER_PORT'])

SOCKET_MSG = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SOCKET_MSG.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
SOCKET_MSG.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

def tratar_cliente(client: socket.socket, addr: tuple) -> None:
    global connected_users
    
    print('Client', addr, 'connected')

    client.send("Digite seu usuário: ".encode())
    username = client.recv(256).decode('utf8').replace('\n', '')

    if username in connected_users:
        client.send("Usuário já registrado".encode())
        client.close()
        exit(1)
    else:
        client.send("OK\x01".encode())

    connected_users.append(username)

    print('Client', addr, 'registered as', username)

    client.send(str(len(connected_users)).encode())

    while True:
        msg = client.recv(2048)

        if msg.decode() == "exit\x01":
            print('Usuário', username, 'saiu do chat')
            connected_users.remove(username)
            break

        data = f"[ {username} ({dt.now()}) ]: {msg.decode()}"
        
        print(data)

        pkt = {'sender': username, 'data': data}

        SOCKET_MSG.sendto(pickle.dumps(pkt), (MULTICAST_GROUP, MULTICAST_PORT))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sockfd:
    sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockfd.bind((SERVER_IP, SERVER_PORT))

    sockfd.listen()

    while True:
        print('Esperando clientes')

        client, addr = sockfd.accept()

        Thread(target=tratar_cliente, args=(client, addr)).start()

        