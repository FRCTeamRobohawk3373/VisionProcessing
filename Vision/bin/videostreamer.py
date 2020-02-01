import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('10.11.4.72', 10000)
print('Starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

while True:
    data, address = sock.recvfrom(4096)
