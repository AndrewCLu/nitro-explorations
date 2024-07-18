from flask import Flask, request, jsonify
from flask_cors import CORS

import socket
import json

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return jsonify(message="Hello, World!")

@app.route('/get-enclave-key')
def get_enclave_key():
    # Create a vsock socket object
    s = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
    
    # Fixed CID for the enclave
    cid = 16

    # The port should match the server running in enclave
    port = 5000

    # Connect to the server
    s.connect((cid, port))

    # Send command to the server running in enclave
    s.send(str.encode(json.dumps({
        'action': 'get-attestation-doc'
    })))

    # Receive and decode response from the server
    payload = s.recv(65536)
    request = json.loads(payload.decode())

    # Get attestation document as a base64 encoded string
    attestation_doc_b64 = request['attestation_doc_b64']

    # Close the connection 
    s.close()

    # Return the attestation document
    return jsonify(attestation_doc=attestation_doc_b64)

@app.route('/send-encrypted-data', methods=['POST'])
def send_encrypted_data():
    try:
        # Get encrypted data from request
        data = request.json.get('data')
        if not data:
            return jsonify({}), 400
        print("Encrypted data: ", data)

        # Create a vsock socket object
        s = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
        
        # Fixed CID for the enclave
        cid = 16

        # The port should match the server running in enclave
        port = 5000

        # Connect to the server
        s.connect((cid, port))

        # Send command to the server running in enclave
        s.send(str.encode(json.dumps({
            'action': 'send-encrypted-data',
            'data': data
        })))

        # Receive and decode response from the server
        payload = s.recv(65536)
        response = json.loads(payload.decode())

        # Get decrypted data from the response
        decrypted_data = response.get('decrypted_data')

        print("Decrypted data: ", decrypted_data)

        # Close the connection 
        s.close()

        # Return the decrypted data
        return jsonify(decrypted_data=decrypted_data), 200
    except Exception as e:
        print(e)

        # Return error response
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)