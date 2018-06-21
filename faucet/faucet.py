from flask import Flask
import requests
import os
import json

app = Flask(__name__)


class Faucet:
    def __init__(self, account_pkey, wallet_url, node_url):
        self.account_pkey = account_pkey
        self.wallet_url = wallet_url
        self.node_url = node_url

    def login_to_wallet(self):
        requests.get(f'{self.wallet_url}/{self.account_pkey}')

    def send_coins(self, account_id, amount):
        self.login_to_wallet()

        response = requests.post(f'{self.wallet_url}/transactions/sign', data=json.dumps({
            'to': account_id,
            'value': amount,
            'fee': 0,
            'data': 'account powering up'
        }))

        transaction = response.content

        requests.post(f'{self.node_url}/transactions/send', data=json.dumps(transaction))

        return '', 200


account_pkey = os.getenv('ACCOUNT_PKEY', '0x7a4045886a916843a9b3e0c89c2f6b28070e056895a722755feb9c6eb442fdbf')
node_url = os.getenv('NODE_URL', '127.0.0.1:5001')
wallet_url = os.getenv('WALLET_URL', '127.0.0.1:5002')

f = Faucet(account_pkey, node_url, wallet_url)


@app.route('/faucet/<account_id>', methods=['GET'])
def send_coins(account_id):
    f.send_coins(account_id, 5)


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    # private key: 0x7a4045886a916843a9b3e0c89c2f6b28070e056895a722755feb9c6eb442fdbf
    # public key: 0xf200862d9dad2074e91869e21f7b5a6aab53f552105fd56faa9c63418eec170ec7efe17e92ae43ca87381b0a5beab5a78993dc9a4f80361316a946709ced82b9
    # address: 0x6Dc9cE392cE48118e8daaB7c78866651a31D4031

    app.run(host='0.0.0.0', port=port)
