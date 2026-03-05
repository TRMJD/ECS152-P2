# client 
# sends messages to proxy server and awaits response
import socket
import json

PROXYHOST = "127.0.0.1"
PROXYPORT = 8080

# create client socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connect to proxy server
client_socket.connect((PROXYHOST, PROXYPORT))

# send message to proxy server in JSON format
def send_message(server_ip: str, server_port: int, message: str):
    # check if message is 4 characters long
    if len(message) != 4:
        print("Error: Message must be 4 characters long")
        return None
    # create JSON payload with server_ip, server_port, and message
    payload = {
        "server_ip": server_ip,
        "server_port": server_port,
        "message": message
    }
    # new connection per request
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((PROXYHOST, PROXYPORT)) # connect to proxy server
        client_socket.sendall(json.dumps(payload).encode("utf-8")) # send JSON payload to proxy server
        # receive response from proxy server
        response = client_socket.recv(4096).decode("utf-8")
        print(f"Response from Proxy: {response}")
        return response

# main loop that reiterates sending messages
while True:
    server_ip = input("Enter server IP address")  
    server_port = input("Enter server port: ")
    message = input("Enter 4 character message: ")
    send_message(server_ip, int(server_port), message)