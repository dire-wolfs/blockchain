import binascii
from eth_keys import keys
import os
import json
from time import time
import hashlib
from flask import Flask, jsonify, request
import requests


class Wallet(object):
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.address = None

    def store(self, private_key, public_key, address):
        self.private_key = private_key.to_hex()
        self.public_key = public_key.to_hex()
        self.address = address

    def generate_new_wallet(self):
        private_key = keys.PrivateKey(os.urandom(32))
        public_key = private_key.public_key
        address = public_key.to_checksum_address()
        self.store(private_key, public_key, address)

        return self.private_key, self.public_key, self.address

    def open_wallet(self, wallet):
        wallet = binascii.unhexlify(wallet[2:])
        private_key = keys.PrivateKey(wallet)
        public_key = private_key.public_key
        address = public_key.to_checksum_address()
        self.store(private_key, public_key, address)

        return self.private_key, self.public_key, self.address

    def sign_transaction(self, to, value, fee, data):
        transaction = {
            'from': self.address,
            'to': to,
            'value': value,
            'fee': fee,
            'timestamp': time(),
            'data': data
        }

        private_key = keys.PrivateKey(binascii.unhexlify(self.private_key[2:]))
        message = hashlib.sha256(json.dumps(transaction).encode('utf8')).digest()
        signature = private_key.sign_msg(binascii.hexlify(message))

        transaction['sender_signature'] = signature.to_hex()
        transaction['data_hash'] = binascii.hexlify(message).decode('utf8')

        return json.dumps(transaction)

    @staticmethod
    def verify_transaction(transaction):
        signed_transaction = transaction
        signature = keys.Signature(binascii.unhexlify(signed_transaction['sender_signature'][2:]))
        public_key = signature.recover_public_key_from_msg(signed_transaction['data_hash'].encode('utf8'))

        signer_address = public_key.to_checksum_address()

        return signer_address == signed_transaction['from']

    def show_balance(self):
        node_url = os.getenv('NODE_URL', '127.0.0.1:5000')
        response = requests.get(f'http://{node_url}/transactions')

        if response.status_code != 200:
            return 'Error on getting transactions', 400
        transactions = response.json()
        balance = 0

        for transaction in transactions:
            if self.address == transaction['to']:
                balance += int(transaction['value'])
            if self.address == transaction['from']:
                balance -= int(transaction['value'])

        return balance


app = Flask(__name__, static_url_path='/static')

wallets = {}


def get_wallet(ip) -> Wallet:
    if wallets.get(ip):
        return wallets.get(ip)

    wallets[ip] = Wallet()
    return wallets.get(ip)


@app.route('/account/<account_id>', methods=['GET'])
def load_account(account_id):
    w = get_wallet(request.remote_addr)
    wallet = w.open_wallet(account_id)

    response = {
        'private_key': wallet[0],
        'public_key': wallet[1],
        'address': wallet[2]
    }

    return jsonify(response), 201


@app.route('/account', methods=['GET'])
def get_account():
    w = get_wallet(request.remote_addr)

    response = {
        'private_key': w.private_key,
        'public_key': w.public_key,
        'address': w.address
    }
    return jsonify(response), 200


@app.route('/account', methods=['POST'])
def new_account():
    w = get_wallet(request.remote_addr)
    wallet = w.generate_new_wallet()

    response = {
        'private_key': wallet[0],
        'public_key': wallet[1],
        'address': wallet[2]
    }

    return jsonify(response), 201


@app.route('/account', methods=['DELETE'])
def forget_account():
    del wallets[request.remote_addr]

    return '', 204


@app.route('/transactions/send', methods=['POST'])
def transaction_send():
    w = get_wallet(request.remote_addr)
    values = request.get_json()

    if not w.private_key or not values:
        return 'No account bound', 400

    required = ['to', 'value', 'fee', 'data']
    if not all(k in values for k in required):
        return 'Missing values', 400

    transaction = w.sign_transaction(values['to'], values['value'], values['fee'], values['data'])

    return transaction, 201


@app.route('/transactions/verify', methods=['POST'])
def transaction_verify():
    values = request.get_json()
    #
    # if not w.private_key:
    #     return 'No account bound', 400

    required = ['data_hash', 'sender_signature', 'from']
    if not all(k in values for k in required):
        return 'Missing values', 400

    is_valid = Wallet.verify_transaction(values)

    response = {
        'valid': is_valid
    }
    return jsonify(response), 200


@app.route('/balance', methods=['GET'])
def get_balance():
    w = get_wallet(request.remote_addr)

    response = {
        "balance": w.show_balance()
    }

    return jsonify(response), 200


@app.route('/dump', methods=['GET'])
def dump():
    print(wallets)

    return jsonify(''), 200


@app.route('/')
def root():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=4000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)

    # w.open_wallet('0x8a93f3a4a1fdf86f3e0453af4110ad83ef779cd315dbd26ca35afc33ac7c20a1')
    # print('new address: ', w.address)
    # r = w.sign_transaction('0xaF788ab8447023e6b790461968A282123C6eAd67', 4, 1, 'no data')
    # print('valid: ', w.verify_transaction(json.loads(r)))
