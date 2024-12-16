import os
import time
import socket
import threading
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Bluetooth addresses of the devices
peer_addr = "B0:C0:90:6A:36:08"
local_addr = "48:E7:DA:F5:29:AC"

# Communication channel
port = 30

base_folder = "./test"

class FolderSyncHandler(FileSystemEventHandler):
    def __init__(self, base_folder, peer_addr, port):
        self.base_folder = base_folder
        self.peer_addr = peer_addr
        self.port = port

    def on_modified(self, event):
        if not event.is_directory:
            send_file(event.src_path, self.base_folder, self.peer_addr, self.port)

    def on_created(self, event):
        if not event.is_directory:
            send_file(event.src_path, self.base_folder, self.peer_addr, self.port)

def send_file(file_path, base_folder, peer_addr, port):
    try:
        relative_path = os.path.relpath(file_path, base_folder)
        with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as sock:
            sock.connect((peer_addr, port))
            with open(file_path, 'rb') as f:
                sock.sendall(relative_path.encode() + b'\n')
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    sock.sendall(data)
    except Exception as e:
        # print(f"Failed to send file {file_path}: {e}")
        pass

def start_server(local_addr, port, base_folder):
    sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    sock.bind((local_addr, port))
    sock.listen(1)

    while True:
        client_sock, address = sock.accept()
        try:
            data = client_sock.recv(1024).decode().split('\n', 1)
            relative_path = data[0]
            file_path = os.path.join(base_folder, relative_path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                while True:
                    data = client_sock.recv(1024)
                    if not data:
                        break
                    f.write(data)
            # print(f"Received file {relative_path} from {address[0]}")
        except Exception as e:
            pass
            # print(f"Error receiving file: {e}")
        finally:
            client_sock.close()

# Start the server thread
server_thread = threading.Thread(target=start_server, args=(local_addr, port, base_folder))
server_thread.daemon = True
server_thread.start()

# Set up folder monitoring
event_handler = FolderSyncHandler(base_folder, peer_addr, port)
observer = Observer()
observer.schedule(event_handler, base_folder, recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()

sys.exit()