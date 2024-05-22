from flask import Flask, jsonify, request
import sys

app = Flask(__name__)
peers = set()

@app.route('/register', methods=['POST'])
def register():
    address = request.form.get('address') or (request.json and request.json.get('address'))
    if not address:
        return jsonify({'message': 'Address is required.'}), 400
    if address not in peers:
        peers.add(address)
        app.logger.info(f'Node registered: {address}')
        return jsonify({'message': 'Node registered successfully.', 'peers': list(peers)}), 200
    app.logger.warning(f'Node already registered: {address}')
    return jsonify({'message': 'Node already registered.'}), 400

@app.route('/unregister', methods=['POST'])
def unregister():
    address = request.form.get('address') or (request.json and request.json.get('address'))
    if not address:
        return jsonify({'message': 'Address is required.'}), 400
    if address in peers:
        peers.remove(address)
        app.logger.info(f'Node unregistered: {address}')
        return jsonify({'message': 'Node unregistered successfully.', 'peers': list(peers)}), 200
    app.logger.error(f'Node not found: {address}')
    return jsonify({'message': 'Node not found.'}), 404

@app.route('/list', methods=['GET'])
def list_peers():
    app.logger.info(f'Current peers list requested.')
    return jsonify(list(peers)), 200

if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8010  # Default port
    app.run(host='0.0.0.0', port=port, debug=True)
