# acts an an intermediary between client and server
# receives request from client, forwards to server, receives response from server, forwards to client
# if packet is ping, respond with pong
import socket
import json # for JSON formatting of messages

# sources used : https://www.youtube.com/watch?v=Ve94yNM0OCU

# function to handle client requests with influence from source
def handle_client(client_socket):
    # receive JSON request from client
    raw = client_socket.recv(4096).decode("utf-8")
    print(f"Received request: {raw}")

    try:
        data = json.loads(raw)
        server_ip = data["server_ip"]
        server_port = int(data["server_port"])
        message = data["message"]
    except (json.JSONDecodeError, KeyError, ValueError):
        client_socket.sendall(b"Bad Request")
        client_socket.close()
        return

    # check blocklist against server_ip
    if server_ip in blocklist:
        reply = "Blocklist Error"
        client_socket.sendall(reply.encode("utf-8"))
        print(f"Blocked server_ip {server_ip}. Sent to client: {reply}")
        client_socket.close()
        return

    # forward ONLY message to server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.connect((server_ip, server_port))
        server_socket.sendall(message.encode("utf-8"))

        # receive response from server
        response = server_socket.recv(4096).decode("utf-8")
        print(f"Received response from server: {response}")

        # forward response back to client
        client_socket.sendall(response.encode("utf-8"))
        print(f"Sent response to client: {response}")

    finally:
        server_socket.close()
        client_socket.close()

# blocklist of IP addresses
blocklist = {
    "192.168.1.100",
    "192.168.1.101"
}

# create proxy socket object
proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# allow reuse of address to avoid "Address already in use" error when restarting server for debugging
proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# bind the socket to a specific address and port
proxy_socket.bind(('localhost', 8080))
# listen for incoming connections
proxy_socket.listen(5) # up to 5 simulataneous connections 
print("Proxy server is listening on port 8080...")

# start main loop to accept incoming connections
while True: 
    # accept connection from client
    client_socket, client_address = proxy_socket.accept()
    print(f"Connection from {client_address} has been established.")
    
    # check if IP address in blocklist
    if client_address[0] in blocklist:
        print(f"Connection from {client_address} is blocked.")
        client_socket.close()
        continue
    
    # handle client request
    handle_client(client_socket)




