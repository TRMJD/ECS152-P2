# server client 
# reverses 4 character messages and transforms "Ping" to "Pong" and "Pong" to "Ping"
import socket

HOST = "127.0.0.1"
PORT = 9090

# helper to print output in required format
def print_header(title: str):
    print("----------------------------")
    print(title)
    print("----------------------------")

# transform message 
def transform_message(message: str) -> str:
    if message == "Ping":
        return "Pong"
    if message == "Pong":
        return "Ping"
    # reverse the 4 characters
    return message[::-1] 

# create server socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # allow reuse of address
server_socket.bind((HOST, PORT))
server_socket.listen(3)
print("Server is listening on port 9090...")

# start main loop to accept incoming connections
while True:
    connection, address = server_socket.accept()
    print(f"Connection from {address} has been established.")
    # receive message from client
    message = connection.recv(4096)
    if not message:
        connection.close()
        continue

    # decode message from bytes to string and print it
    message = message.decode("utf-8")
    print_header("Received from Proxy:")
    print(f'"{message}"')

    # transform message and send response back to proxy
    response = transform_message(message)

    # print what we are sending to proxy (after response is computed)
    print_header("Sent to Proxy:")
    print(f'"{response}"')

    connection.sendall(response.encode("utf-8")) # send response back to proxy
    connection.shutdown(socket.SHUT_WR) # signal no more data to send
    
    connection.close()