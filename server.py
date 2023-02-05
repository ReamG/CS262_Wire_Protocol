import socket
import threading

HOST = "localhost"
PORT = 65432

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((HOST, PORT))
serversocket.listen(5)

while True:
  # accept connections from outside
  (clientsocket, address) = serversocket.accept()
  print(clientsocket, address)
