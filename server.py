#!/usr/bin/env python3

import socket
import os

from util import cria_mensagem
from threading import Thread

CONNECTED_USERS = dict()

SERVER_IP = str(os.environ['SERVER_IP'])
SERVER_PORT = int(os.environ['SERVER_PORT'])

def broadcast(mensagem: str, client: socket.socket) -> None:
    c: socket.socket

    for user, c in CONNECTED_USERS.items():
        if c != client:
            try:
                c.send(mensagem)
            except:
                c.close()
                remover_cliente(user)

def remover_cliente(user: str) -> None:
    global CONNECTED_USERS

    if user in CONNECTED_USERS:
        CONNECTED_USERS.pop(user)


def tratar_cliente(client: socket.socket, addr: tuple) -> None:
    global CONNECTED_USERS
    
    print('Client', addr, 'connected')

    client.send("Digite seu usuário: ".encode())
    username = client.recv(256).decode('utf8').replace('\n', '')

    if username in CONNECTED_USERS:
        client.send("Usuário já registrado".encode())
        client.close()
        exit(1)
    else:
        client.send("OK\x01".encode())

    CONNECTED_USERS[username] = client

    print('Client', addr, 'registered as', username)

    client.send(str(len(CONNECTED_USERS)).encode())

    while True:
        msg = client.recv(2048).decode('utf8')

        if msg == "exit\x01" or not msg:
            msg = f"Usuário {username} saiu do chat"
            msg = cria_mensagem("Servidor", msg)
            print(msg.decode())
            broadcast(msg, client)
            remover_cliente(username)
            break
        
        msg = cria_mensagem(username, msg)
        print(msg.decode())

        broadcast(msg, client)

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sockfd:
        sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sockfd.bind((SERVER_IP, SERVER_PORT))

        sockfd.listen()

        while True:
            print('Esperando clientes')

            client, addr = sockfd.accept()

            Thread(target=tratar_cliente, args=(client, addr)).start()

        