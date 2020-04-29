#!/usr/bin/env python3
import bluetooth
import time

server_socket = bluetooth.BluetoothSocket( bluetooth.RFCOMM)
print("Bluetooth connected")

port = 1
server_socket.bind(("",port))
server_socket.listen(1)

client_socket,address = server_socket.accept()
print ('Accepted connection from')

data = ''

while 1:
    data = client_socket.recv(1024)
    print(data)
    time.sleep(1)

client_socket.close()
server_socket.close()