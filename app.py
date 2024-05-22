import argparse
from flask import Flask, jsonify, request, render_template
from uuid import uuid4
import requests
import time
from blockchain import Blockchain
from p2p_node import P2PNode

parser = argparse.ArgumentParser(description="Run the Flask and P2P node servers.")
parser.add_argument('--flask_port', type=int, default=5000, help="Port for the Flask server to listen on.")
parser.add_argument('--p2p_port', type=int, default=5001, help="Port for the P2P node to listen on.")
args = parser.parse_args()

app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()
p2p_node = None
registered = False

def create_p2p_node():
    global p2p_node
    if not p2p_node:
        p2p_node = P2PNode(blockchain, '0.0.0.0', args.p2p_port, f'http://127.0.0.1:{args.flask_port}')

def register_with_tracker():
    global registered
    if registered:
        print("Already registered with the tracker.")
        return  # Skip registration if already registered
    
    #### FIX IN HERE THAT THE PORT NUMBER YOU USED #####
    tracker_url = 'http://127.0.0.1:5001/register' # for example: 8813 you used in track.py 8113
    my_address = f'http://127.0.0.1:{args.flask_port}'
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            response = requests.post(tracker_url, json={'address': my_address})
            if response.status_code == 200:
                print("Registered with tracker successfully.")
                registered = True
                create_p2p_node()  # Initialize P2P node only after successful registration
                return
            else:
                print(f"Failed to register with tracker. Status Code: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            print(f"Attempt {attempt + 1}: Could not connect to the tracker: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
    print("Failed to register with the tracker after several attempts.")
# Flask routes setup as before...

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    blockchain.new_transaction(sender="0", recipient=node_identifier, amount=1)
    previous_hash = Blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)
    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response)

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response)

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response)

@app.route('/reset', methods=['POST'])
def reset_blockchain():
    blockchain.__init__()  # Reinitialize the blockchain
    return jsonify({'message': 'Blockchain has been reset'}), 200

if __name__ == '__main__':
    register_with_tracker()
    app.run(host='0.0.0.0', port=args.flask_port)
