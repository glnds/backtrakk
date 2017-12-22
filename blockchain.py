import hashlib
import json
from time import time


class Blockchain(object):
    # """A Simple blockchain"""

    def __init__(self):
        self.chain = []
        self.unconfirmed_txns = []

        # Create the genesis block
        self.new_block(proof=100, previous_hash=1)

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
            'txns': self.unconfirmed_txns,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
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

    @staticmethod
    def hash(block):
        """
        Create a SHA-256 hash of a block.

        :param block: <dict> Block
        :return: <str> Hash of a block
        """

        # Ensure the dictionary is sorted for hash consistency
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """Return the last block of the blockchain."""
        return self.chain[-1]
