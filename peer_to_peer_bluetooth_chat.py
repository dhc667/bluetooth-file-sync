import socket
import threading
import sys

### Requisitos
## Es necesario tener emparejados a nivel de sistema operativo los dos dispositivos bluetooth
## y conocer de antemano sus direcciones MAC.

peer_addr = "B8:27:EB:10:BB:88"
local_addr = "2C:0D:A7:6F:99:C8"

username = ""

# Canal de comunicación empleado por Bluetooth, valor entre 1 y 30
port = 30

def start_server(local_addr, port):

    sock= socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    sock.bind((local_addr,port))
    sock.listen(1)

    while True:
        client_sock,address = sock.accept()
        data = client_sock.recv(1024)

        user_name = data.decode().split('::')
        print(f"device: {address[0]} port: {address[1]} username: {user_name[0]}: {user_name[1]}")
        client_sock.close()

def send_message(message, name, peer_addr, port):
    with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as sock:
        sock.connect((peer_addr, port))
        sock.send(f"{name}::{message}".encode())

# Hilo que se encarga de manejar los mensajes entrantes

server = threading.Thread(target=start_server, args=(local_addr,port,))
server.daemon = True
server.start()

username = input("Inserte su nombre de usuario: ")

while True:
    message = input("> ")
    if not message or not len(message):
        server_enabled = False
        break
    send_message(message, username, peer_addr, port)

sys.exit()