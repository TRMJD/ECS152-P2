# server client 
# reverses 4 character messages and transforms "Ping" to "Pong" and "Pong" to "Ping"
import socket

HOST = "127.0.0.1"
PORT = 9090

# transform message 
def transform_message(message: str) -> str:
    if message == "Ping":
        return "Pong"
    if message == "Pong":
        return "Ping"
    # reverse the 4 characters
    return message[::1] 

# create server socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
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
    print(f"Received message from Proxy: {message}")

    response = transform_message(message)
    print(f"Transformed message to: {response}")
    connection.sendall(response.encode("utf-8")) # send response back to proxy
    print(f"Sent response back to Proxy: {response}")
    connection.close()


