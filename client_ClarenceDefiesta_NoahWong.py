# client 
# sends messages to proxy server and awaits response
import socket
import json

PROXYHOST = "127.0.0.1"
PROXYPORT = 8080

# formatting functions
def print_header(title: str):
    print("----------------------------")
    print(title)
    print("----------------------------")

def print_data_block(server_ip: str, server_port: int, message: str):
    print('data = {')
    print(f'"server_ip": "{server_ip}"')
    print(f'"server_port": {server_port}')
    print(f'"message": "{message}"')
    print('}')

# send message to proxy server in JSON format
def send_message(server_ip: str, server_port: int, message: str):
    # check if message is 4 characters long
    while len(message) != 4:
        print("Message must be exactly 4 characters long.")
        message = input("Enter 4 character message: ")

    # create JSON payload with server_ip, server_port, and message
    payload = {
        "server_ip": server_ip,
        "server_port": server_port,
        "message": message
    }

    # new connection per request
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((PROXYHOST, PROXYPORT)) # connect to proxy server

        # print header and data block
        print_header("Sent to Proxy:")
        print_data_block(server_ip, server_port, message)

        s.sendall(json.dumps(payload).encode("utf-8")) # send JSON payload to proxy server
        s.shutdown(socket.SHUT_WR) # signal no more data to send

        # receive response from proxy server
        response = s.recv(4096).decode("utf-8")

        # print in formatted style 
        print_header("Received from Proxy:")
        print(f'"{response}"')

# main loop that reiterates sending messages
while True:
    server_ip = input("Enter server IP address: ").strip()
    server_port = int(input("Enter server port: ").strip())
    message = input("Enter 4 character message: ").strip()
    send_message(server_ip, server_port, message)