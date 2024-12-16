import os
import time
import socket
import threading
import shutil

def get_files_with_timestamps(folder):
    files = {}
    for root, _, filenames in os.walk(folder):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            relative_path = os.path.relpath(full_path, folder)
            files[relative_path] = os.path.getmtime(full_path)  # Last modified time
    return files

def send_file(sock, file_path, base_folder):
    try:
        relative_path = os.path.relpath(file_path, base_folder)
        with open(file_path, 'rb') as f:
            sock.sendall(relative_path.encode() + b'\n')
            while True:
                data = f.read(1024)
                if not data:
                    break
                sock.sendall(data)
    except Exception as e:
        print(f"Failed to send file {file_path}: {e}")

def start_server(host, port, base_folder):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        threading.Thread(target=handle_client, args=(client_socket, base_folder)).start()

def handle_client(client_socket, base_folder):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            # Handle received data
            print(f"Received data: {data}")
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

def connect_to_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    return client_socket

# Example usage
if __name__ == "__main__":
    base_folder = "/path/to/folder"
    host = "localhost"
    port = 12345

    # Start server in a separate thread
    threading.Thread(target=start_server, args=(host, port, base_folder)).start()

    # Connect to server and send a file
    time.sleep(1)  # Wait for server to start
    client_socket = connect_to_server(host, port)
    send_file(client_socket, "/path/to/file.txt", base_folder)
    client_socket.close()