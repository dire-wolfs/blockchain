import threading
from uuid import uuid4
import hashlib
from time import sleep, gmtime
import requests
import os


# TODO: fix prints with logging

class Block(object):
    def __init__(self, index, data_hash, difficulty):
        self.index = index
        self.data_hash = data_hash
        self.difficulty = difficulty

        self.hash = 0
        self.timestamp = gmtime()
        self.nonce = 0
        self.terminated = False


class Miner():
    def __init__(self, node_url, address):
        self.node_url = node_url
        self.id = str(uuid4()).replace('-', '')
        self.address = address

    def run(self):
        while True:

            block = self.get_job()
            if not block:
                continue

            t = threading.Thread(target=Miner.mine, args=(block,))
            t.start()

            while t.is_alive():
                # check every 3 seconds if we mine something old
                sleep(3)
                index = self.get_last_block_index()

                if index >= block.index:
                    block.terminated = True

                    print("We are working on old block %s! Current block index %s", block.index, index)
                    break
                else:
                    print('Still on the active block!')

            if block.terminated:
                print(block.index, block.terminated)
                continue

            self.submit_block(block)
            # wait some time before getting new job
            sleep(5)

    def get_last_block_index(self):
        response = requests.get(f'http://{self.node_url}/blocks/last-block')

        if response.status_code == 200:
            index = response.json()['index']
            return index

        return None

    def get_job(self):

        try:
            response = requests.get(f'http://{self.node_url}/mining/get-mining-job/{self.address}')
        except requests.exceptions.ConnectionError as ce:
            print("Could not get a job")
            print("Sleeping for 60 seconds")
            print(ce.strerror)
            sleep(60)
            return self.get_job()

        if response.status_code == 200:
            block = Block(
                response.json()['index'],
                response.json()['data_hash'],
                response.json()['difficulty']
            )
            print('Got new block %s with index %s', block.data_hash, block.index)
            return block

        print('Could not get a new job! Status code %s', response.status_code)
        return None

    def submit_block(self, block):
        data = {
            'hash': block.hash,
            'timestamp': block.timestamp,
            'nonce': block.nonce
        }
        response = requests.post(f'http://{self.node_url}/mining/submit-mined-block', data)
        if response.status_code == 200:
            print('Block submitted: %s! Returned message: %s', block.index, block.nonce, response.json()['message'])
        else:
            print('Block failed submitting! Status code: %s', response.status_code)

    @staticmethod
    def mine(block):
        print('Starting mining on: %s with index %s', block.data_hash, block.index)
        while True:
            block.timestamp = gmtime()

            block.hash = Miner.hash(block)
            if Miner.is_valid_difficulty(block.hash, block.difficulty):
                break

            block.nonce += 1
            if block.terminated:
                return None

        print('Block successfully mined: %s %s %s', block.hash, block.index, block.nonce)

        return block

    @staticmethod
    def hash(block):
        block_string = f'{block.data_hash}{block.timestamp}{block.nonce}'.encode('utf8')
        return hashlib.sha256(block_string).hexdigest()

    @staticmethod
    def is_valid_difficulty(block_hash, difficulty):
        return int(block_hash[:difficulty], 16) == 0


if __name__ == '__main__':
    node_url = os.getenv('NODE_URL', '127.0.0.1:5000')
    miner_address = os.getenv('MINER_ADDRESS', '64fc78F058E664f8CEceBEA65c03bCe199515c75')

    miner = Miner(node_url, miner_address)
    miner.run()
