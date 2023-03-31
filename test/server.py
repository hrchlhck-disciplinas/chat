import socket
import struct

from ipaddress import ip_address

class Sniffer:
    def __init__(self, iface: str):
        self._iface = iface

    def get_ip_header(self):
        fields = ['hl', 'tos', 'len', 'id', 'off', 'ttl', 'proto', 'checksum', 'src', 'dst']

        data, _ = self._fd.recvfrom(512)

        header_data = struct.unpack("!BBHHHBBHII", data[14:34])

        ret = dict(zip(fields, header_data))
        ret['src'] = str(ip_address(ret['src']))
        ret['dst'] = str(ip_address(ret['dst']))
        return ret
    
    def __enter__(self):
        self._fd = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x0800))

    def __exit__(self, *args):
        self._fd.close()


if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s, Sniffer("eth0") as sniffer:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            s.bind(('0.0.0.0', 8888))

            s.listen()

            while True:
                print('[+] Waiting connections')
                conn, addr = s.accept()

                str_addr = ':'.join(map(str, addr))

                print(f"[+] Client {str_addr} connected")

                
                while True:
                    try:
                        data = conn.recv(1024)
                        print(sniffer.get_ip_header())

                        if not data:
                            print(f'[-] Client {str_addr} exited')
                            break
                        
                        print(f"[+] {str_addr} ->", data.decode())
                    except Exception as e:
                        print('[-] Client exited with error', e)
                        break