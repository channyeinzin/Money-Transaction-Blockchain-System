import socket
import threading
import requests
import json

from blockchain import Blockchain

class P2PNode:
    def __init__(self, blockchain, host, port, tracker_url):
        self.blockchain = blockchain
        self.host = host
        self.port = port
        self.tracker_url = tracker_url
        self.peers = set()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(10)
        threading.Thread(target=self.listen_for_incoming_connections).start()
        self.register_with_tracker()

    def listen_for_incoming_connections(self):
        while True:
            client_socket, address = self.server.accept()
            threading.Thread(target=self.handle_client, args=(client_socket, address)).start()

    def handle_client(self, client_socket, address):
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message:
                    self.process_message(message, client_socket)
                else:
                    break
            except Exception as e:
                print(f"Error handling data from {address}: {e}")
                break
        client_socket.close()

    def register_with_tracker(self):
        response = requests.post(f'{self.tracker_url}/register', data={'address': f'{self.host}:{self.port}'})
        if response.status_code == 200:
            self.peers.update(response.json()['peers'])
        self.update_peers()

    def unregister_with_tracker(self):
        requests.post(f'{self.tracker_url}/unregister', data={'address': f'{self.host}:{self.port}'})
        self.server.close()

    def update_peers(self):
        response = requests.get(f'{self.tracker_url}/list')
        if response.status_code == 200:
            new_peers = set(response.json())
            self.peers.update(new_peers)

    def broadcast(self, message, exclude=None):
        for peer in self.peers:
            if peer != exclude:
                try:
                    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    peer_socket.connect((peer))
                    peer_socket.sendall(message.encode('utf-8'))
                    peer_socket.close()
                except:
                    self.peers.remove(peer)

    def process_message(self, message, client_socket):
        print(f"Processing message: {message}")
        data = json.loads(message)
        if data['type'] == 'new_block':
            # Validate and add block
            pass
        elif data['type'] == 'new_transaction':
            # Validate and add transaction
            pass

if __name__ == '__main__':
    import sys
    host = '0.0.0.0'
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    tracker_url = 'http://localhost:5001'
    blockchain = Blockchain()  # Assuming Blockchain class is properly implemented
    node = P2PNode(blockchain, host, port, tracker_url)
