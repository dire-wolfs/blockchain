from uuid import uuid4
import hashlib
from time import time, sleep
import requests
import os


class Block(object):
    def __init__(self, data_hash, difficulty):
        self.data_hash = data_hash
        self.difficulty = difficulty
        self.hash = 0
        self.date_created = time()
        self.nonce = 0


class Miner(object):
    def __init__(self, node_url, address):
        self.node_url = node_url
        self.id = str(uuid4()).replace('-', '')
        self.address = address

    def run(self):
        while True:
            self.get_job()
            sleep(2)

    def get_job(self):
        response = requests.get(f'http://{self.node_url}/mining/get-mining-job/{self.address}')

        if response.status_code == 200:
            block = Block(response.json()['data_hash'], response.json()['difficulty'])
            print(f'[{block.date_created}]: got new job: {block.data_hash}')
            mined_block = Miner.mine(block)

            self.submit_block(mined_block)
        else:
            print(f'[{time()}]: could not get a job! Status code: {response.status_code}')

    def submit_block(self, block):
        data = {
            'hash': block.hash,
            'date_created': block.date_created,
            'nonce': block.nonce
        }
        response = requests.post(f'http://{self.node_url}/mining/submit-mined-block', data)
        if response.status_code == 200:
            print(f'[{time()}]: block submitted: ', response.json()['message'])
        else:
            print(f'[{time()}]: block failed submitting! Status code: ', response.status_code)

    @staticmethod
    def mine(block):
        while True:
            block.date_created = time()

            block.hash = Miner.hash(block)
            if Miner.is_valid_difficulty(block.hash, block.difficulty):
                break
            block.nonce += 1

        print(f'[{time()}]: block mined: ', block.hash)

        return block

    @staticmethod
    def hash(block):
        block_string = f'{block.data_hash}{block.date_created}{block.nonce}'.encode('utf8')
        return hashlib.sha256(block_string).hexdigest()

    @staticmethod
    def is_valid_difficulty(block_hash, difficulty):
        return int(block_hash[:difficulty], 16) == 0


if __name__ == '__main__':
    node_url = os.getenv('NODE_URL', '127.0.0.1:5000')
    miner_address = os.getenv('MINER_ADDRESS', '1F1tAaz5x1HUXrCNLbtMDqcw6o5GNn4xqX')

    miner = Miner(node_url, miner_address)
    miner.run()
