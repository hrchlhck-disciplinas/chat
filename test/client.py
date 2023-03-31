import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('172.17.0.2', 8888))

    print('[+] Connected to server')

    while True:
        try:
            # Change TTL
            s.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, 128)
            data = input('>>> ').encode()
            s.send(data)
        except Exception as e:
            print('[-] Client exited with error', e)
            break
