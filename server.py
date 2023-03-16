#!/usr/bin/env python3

import socket
import pickle
import os

from datetime import datetime as dt
from threading import Thread

connected_users = dict()

MULTICAST_GROUP = str(os.environ['MULTICAST_GROUP'])
MULTICAST_PORT = int(os.environ['MULTICAST_PORT'])

SERVER_IP = str(os.environ['SERVER_IP'])
SERVER_PORT = int(os.environ['SERVER_PORT'])

AUTHENTICATE = str(os.environ['AUTHENTICATE'])

SOCKET_MSG = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SOCKET_MSG.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
SOCKET_MSG.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

def cadastrar_cliente(client: socket.socket) -> None:
    pass

def autenticar_cliente(client: socket.socket) -> str:
    global connected_users

    client.send("Digite seu usuário: ".encode())
    username = client.recv(256).decode('utf8')

    if username in connected_users:
        client.send("Usuário já registrado".encode())
        client.close()
        exit(1)
        
    if AUTHENTICATE != "yes":
        client.send("OK\x01".encode())
        connected_users[username] = ""
    else:
        client.send("Digite sua senha: ".encode())
        passwd = client.recv(256).decode('utf8')

        if passwd == connected_users.get(username):
            client.send("OK\x01".encode())
        else:
            client.send("INVALID\x01".encode())

    return username


def tratar_cliente(client: socket.socket, addr: tuple) -> None:
    
    print('Client', addr, 'connected')

    username = autenticar_cliente(client)

    print('Client', addr, 'registered as', username)

    client.send(str(len(connected_users)).encode())

    while True:
        msg = client.recv(2048)

        if len(msg) == 0:
            connected_users.pop(username)
            break

        if msg.decode() == "exit\x01":
            data = f"{dt.now().strftime('%d/%m/%Y %H:%M')} [ SERVIDOR ]: Usuário {username} saiu do chat"
            print(data)

            if username in connected_users:
                connected_users.pop(username)

            pkt = {'sender': username, 'data': data}

            SOCKET_MSG.sendto(pickle.dumps(pkt), (MULTICAST_GROUP, MULTICAST_PORT))
            break

        data = f"{dt.now().strftime('%d/%m/%Y %H:%M')} [ {username} ]: {msg.decode()}"
        
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

        