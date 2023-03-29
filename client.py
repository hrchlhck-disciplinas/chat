#!/usr/bin/env python3

import socket
import os
import select
import sys

from util import cria_mensagem

USERNAME = ""

SERVER_IP = str(os.environ['SERVER_IP'])
SERVER_PORT = int(os.environ['SERVER_PORT'])

def tratar_input(addr: tuple):
    global USERNAME
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as fd:
        fd.connect(addr)

        uname = fd.recv(256).decode()
        print(uname)

        msg = input(">>> ")
        fd.send(msg.encode('utf8'))

        confirm = fd.recv(128).decode()

        if confirm != "OK\x01":
            print(confirm)
            exit(1)

        users_online = fd.recv(1).decode()
        print('Users connected:', users_online)

        USERNAME = msg

        while True:
            socket_list = [sys.stdin, fd]

            sockets, _, _ = select.select(socket_list, [], [])

            try:
                for s in sockets:
                    if s == fd:
                        msg = s.recv(2048)
                        print(msg.decode())
                        continue
                    else:
                        
                        msg = sys.stdin.readline()

                        fd.send(msg.replace('\n', '').encode('utf8'))

                        msg = cria_mensagem("Você", msg, net=False)
                        sys.stdout.write(msg)
                        sys.stdout.flush()
            except KeyboardInterrupt:
                fd.send("exit\x01".encode('utf8'))
                break

if __name__ == '__main__':
    print(SERVER_IP, SERVER_PORT)
    tratar_input((SERVER_IP, SERVER_PORT))