"""
Based on https://github.com/richardfan1126/nitro-enclave-python-demo/blob/master/attestation_verifier/server/NsmUtil.py
"""

import socket
import json
import base64
import hashlib
import os

from NsmUtil import NSMUtil

# Add these new functions at the top level
def generate_secret(length=32):
    """Generate a cryptographically secure random secret"""
    return os.urandom(length)

def hash_string(input_string: str, secret: bytes) -> str:
    """Hash a string concatenated with the secret using SHA-256"""
    combined = input_string.encode() + secret
    return hashlib.sha256(combined).hexdigest()

def hash_secret(secret: bytes) -> str:
    """Hash the secret alone using SHA-256"""
    return hashlib.sha256(secret).hexdigest()


def main():
    print("Starting enclave server...")

    # Generate secret when server starts
    server_secret = generate_secret()
    print("Server secret generated")


    # Initialise NSMUtil
    nsm_util = NSMUtil()
    
    # Create a vsock socket object
    client_socket = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)

    # Listen for connection from any CID
    cid = socket.VMADDR_CID_ANY

    # The port should match the client running in parent EC2 instance
    client_port = 5000

    # Bind the socket to CID and port
    client_socket.bind((cid, client_port))

    # Listen for connection from client
    client_socket.listen()

    while True:
        client_connection, addr = client_socket.accept()

        # Get command from client
        payload = client_connection.recv(4096)
        request = json.loads(payload.decode())

        if request['action'] == 'get-attestation-doc':
            # Generate attestation document
            attestation_doc = nsm_util.get_attestation_doc()

            # Base64 encode the attestation doc
            attestation_doc_b64 = base64.b64encode(attestation_doc).decode()

            # Generate JSON attestation response
            attestation_response = json.dumps({
                'attestation_doc_b64': attestation_doc_b64
            })

            # Send response to client
            client_connection.send(str.encode(attestation_response))
        
        # elif request['action'] == 'send-encrypted-data':
        #     encrypted_data = base64.b64decode(request['data'])

        #     # Decrypt the data using the public key
        #     data = nsm_util.decrypt(encrypted_data)

        #     # Log the decrypted data to console
        #     print("New data decryption: ", data)

        #     # Generate JSON response with decrypted data
        #     response = json.dumps({
        #         'decrypted_data': data
        #     })

        #     # Send response back to the client
        #     client_connection.send(str.encode(response))

        elif request['action'] == 'hash-with-secret':
            encrypted_data = base64.b64decode(request['encrypted_input'])

            # Decrypt the data using the public key
            data = nsm_util.decrypt(encrypted_data)
            
            # Hash the input string with the secret
            string_hash = hash_string(data, server_secret)
            secret_hash = hash_secret(server_secret)

            # Generate JSON response
            response = json.dumps({
                'string_hash': string_hash,
                'secret_hash': secret_hash
            })

            # Send response back to the client
            client_connection.send(str.encode(response))

        # Close the connection with client
        client_connection.close()

if __name__ == '__main__':
    main()