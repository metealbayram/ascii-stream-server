import socket
import threading
import time

HOST = '127.0.0.1'
PORT = 65432
NUM_CHANNELS = 3

channels = {
    0: {'clients': [], 'file': '1.txt', 'current_frame': ''},
    1: {'clients': [], 'file': '2.txt', 'current_frame': ''},
    2: {'clients': [], 'file': '4.txt', 'current_frame': ''}
}

channel_locks = [threading.Lock() for _ in range(NUM_CHANNELS)]

def broadcaster(channel_id):
    try:
        with open(channels[channel_id]['file'], 'r') as file:
            while True:
                line = file.readline()
                if not line:
                    file.seek(0)
                    continue

                with channel_locks[channel_id]:
                    channels[channel_id]['current_frame'] = line

                time.sleep(0.05)  # Yayın hızı
    except Exception as e:
        print(f"Error in broadcaster for channel {channel_id+1}: {e}")

def handle_client(client_socket, channel_id):
    print(f"Client connected to channel {channel_id+1}")
    with channel_locks[channel_id]:
        channels[channel_id]['clients'].append(client_socket)

    try:
        while True:
            with channel_locks[channel_id]:
                frame = channels[channel_id]['current_frame']

            if frame:
                try:
                    client_socket.sendall(frame.encode('utf-8'))
                except:
                    break
            time.sleep(0.05)

    except Exception as e:
        print(f"Error sending to client: {e}")
    finally:
        with channel_locks[channel_id]:
            channels[channel_id]['clients'].remove(client_socket)
        client_socket.close()
        print(f"Client disconnected from channel {channel_id+1}")

def client_handler(client_socket):
    try:
        channel_choice = int(client_socket.recv(1024).decode('utf-8').strip())
        if 0 <= channel_choice < NUM_CHANNELS:
            print(f"Client selected channel {channel_choice+1}")
            handle_client(client_socket, channel_choice)
        else:
            client_socket.sendall("Invalid channel. Disconnecting...\n".encode('utf-8'))
            client_socket.close()
    except Exception as e:
        print(f"Client handler error: {e}")
        client_socket.close()

def start_server():
    for channel_id in range(NUM_CHANNELS):
        threading.Thread(target=broadcaster, args=(channel_id,), daemon=True).start()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print("Server started and waiting for connections...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        threading.Thread(target=client_handler, args=(client_socket,), daemon=True).start()

if __name__ == "__main__":
    start_server()
