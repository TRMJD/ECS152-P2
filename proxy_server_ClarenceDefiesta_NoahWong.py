# acts an an intermediary between client and server
# receives request from client, forwards to server, receives response from server, forwards to client
# if packet is ping, respond with pong
import socket
import json # for JSON formatting of messages

# blocklist of IP addresses
blocklist = {
    "192.168.1.100",
    "192.168.1.101"
}

# create proxy socket object
proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a specific address and port
proxy_socket.bind(('localhost', 8080))
# listen for incoming connections
proxy_socket.listen(5)
print("Proxy server is listening on port 8080...")

# start main loop to accept incoming connections
while True: 
    # accept connection from client
    client_socket, client_address = proxy_socket.accept()
    print(f"Connection from {client_address} has been established.")

