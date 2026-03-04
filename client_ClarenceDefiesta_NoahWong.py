# client 
# sends messages to proxy server and awaits response
import socket
import json

HOST =  'localhost'
PORT = 8080
# create client socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connect to proxy server
client_socket.connect((HOST, PORT))

