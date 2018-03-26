import sha3
import json
from time import time
from uuid import uuid4
from urllib.parse import urlparse

from flask import Flask, jsonify, request


class Blockchain(object):
    # """A Simple blockchain"""

    def __init__(self):
        self.chain = []
        self.unconfirmed_txns = []
        self.nodes = set()

        # Create the genesis block
        self.new_block(proof=100, previous_hash=1)

    def register_node(self, address):
        """
        Add a new node

        :param address: <str> Address of the node
        :return: None
        """

        node_url = urlparse(address)
        self.nodes.add(node_url.netloc)

    def valid_chain(self, chain):
        """
        Check if a chain is the longest chain

        :param chain: <list> A blockchain
        :return: <bool> True if chain is the longest one
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # check the block's hash
            if block['previous_hash'] != self.hash(last_block):
                return False

    def new_block(self, proof, previous_hash=None):
        """
        Create a new block and add it to the blockchain.

        :param proof: <int> The proof given by the PoW algorithm
        :param previous_hash: (Optional) <str> Hash of the previous block
        :return: <dict> New block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'nonce': '',
            'miner_address': '',
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            'txns': self.unconfirmed_txns,
        }
        # Clear the list of unconfirmed transactions
        self.unconfirmed_txns = []

        # Append the block to the blockchain
        self.chain.append(block)

        return block

    def new_txn(self, sender, receiver, amount):
        """
        Create a new transaction whick will go to the next mined block.

        :param sender: <str> Address of the sender
        :param receiver: <str> Address of the receiver
        :param amount: <int> Amount
        :return: <int> Index of the block that will hold this transaction
        """

        self.unconfirmed_txns.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    def proof_of_work(self, last_proof):
        """
            Simple Proof of Work algorithm:
            - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
            - p is the previous proof, and p' is the new proof
            :param last_proof: <int> Previous proof
            :return: <int>
        """
        # TODO: should be nonce
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates a proof: does hash(last_proof, proof) contain 4 leading zeroes?

        :param last_proof: <int> Previous proof
        :param proof: <int> Current proof
        :return: <bool> True if correct, False if not.
        """

        # Because SHA3 is designed to be a completely unpredictable pseudorandom function,
        # the only way to create a valid block is simply trial and error, repeatedly incrementing
        # the nonce and check if the new hash matches.
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = sha3.keccak_256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @staticmethod
    def hash(block):
        """
        Create a SHA-256 hash of a block.

        :param block: <dict> Block
        :return: <str> Hash of a block
        """

        # Ensure the dictionary is sorted for hash consistency
        block_string = json.dumps(block, sort_keys=True).encode()
        return sha3.keccak_256(block_string).hexdigest()

    @property
    def last_block(self):
        """Return the last block of the blockchain."""
        return self.chain[-1]


# Flask ########################################################################################
app = Flask(__name__)

# Generate a unique address for this node
node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    """Run the PoW algorithm to get the next proof."""

    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Mining reward
    blockchain.new_txn(
        sender="0",
        receiver=node_identifier,
        amount=1,
    )

    # Confirm the block
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block confirmed",
        'index': block['index'],
        'transactions': block['txns'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    data = request.get_json()
    print(data)

    # Input validation
    mandatory = ['sender', 'receiver', 'amount']
    if not all(key in data for key in mandatory):
        return 'Some fields are missing in the transaction data', 400

    # Create a new transaction
    index = blockchain.new_txn(
        data['sender'], data['receiver'], data['amount'])
    response = {'message': f'Transaction will be added to block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
