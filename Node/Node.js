const Block = require("./Block");
const Transaction = require("./Transaction");
const cryptoTools = require("./utilities/CommonCryptoTools");
const logger = require("./utilities/Logger");

const nullAddress = "0000000000000000000000000000000000000000";
const nullPubKey = "00000000000000000000000000000000000000000000000000000000000000000";
const nullSignature = ["0000000000000000000000000000000000000000000000000000000000000000","0000000000000000000000000000000000000000000000000000000000000000"];
const startDifficulty = 1
const faucetPrivateKey = '838ff8634c41ba62467cc874ca156830ba55efe3e41ceeeeae5f3e77238f4eef';
const faucetPublicKey = cryptoTools.privateKeyToPublicKey(faucetPrivateKey);
const faucetAddress = cryptoTools.publicKeyToAddress(faucetPublicKey);

const genesisDate = 1514764800;
const genesisFaucetTransaction = new Transaction(
	nullAddress,   // from address
	faucetAddress, // to Address
	10000000,      // value of transfer
	0,             // fee for mining
	genesisDate,   // dateCreated
	"genesisTx",   // data (payload)
	nullPubKey,    // senderPubKey
	undefined,     // transactionDataHash
	nullSignature, // senderSignature
	0,             // minedInBlockIndex
	true           // transferSuccessful
);
const genesisBlock = new Block(
	0,           // block index
	genesisDate, // date created
	[genesisFaucetTransaction], // transactions array
	0,           // nonce
	1,           // previous block hash
	0,           // currentDifficulty
	nullAddress, // mined by (address)
	0,           // block data hash
	0            // block hash
);

class Node {
	constructor(genesisBlock, startDifficulty) {
		this.blocks = [genesisBlock];
		this.pendingTransactions = [];
		this.currentDifficulty = startDifficulty;
		this.nodes = [];
		this.ongoingMiningJobs = [];
	}
	
	registerNodes(nodeAddress) {
		//@TODO check if the node address is valid
		this.nodes.push(nodeAddress);
	}
	
	calculateCumulativeDifficulty() {
		let difficulty = 0;
		for (let block of this.blocks) {
			difficulty += 16 ** block.difficulty;
		}
		return difficulty;
	}
	
	getPendingTransactions() {
		return this.pendingTransactions;
	}
	
	getLastBlock() {
		return this.blocks[this.blocks.length - 1];
	}
	
	getMiningJob(minerAddress) {
		let lastBlock = this.getLastBlock();
		let newCandidateBlock = new Block(
			lastBlock.index + 1,
			Date.now(),
			this.getPendingTransactions(),
			undefined, // nonce - calculated from miner
			lastBlock.hash,
			this.currentDifficulty,
			minerAddress,
			undefined, // data hash - calculated in the block object itself
			undefined // final hash - comes from the miner
		);
		
		this.ongoingMiningJobs[newCandidateBlock.dataHash] = newCandidateBlock;
		
		return newCandidateBlock;
	}
	
	receiveMinerData(minerIdentityHash, nonce, minerClaim) {
		if(!this.ongoingMiningJobs[minerIdentityHash]) {
			logger.error('Unknown miner: "' + minerIdentityHash + '"');
			return;
		}
		
		let minerWorkingBlock = this.ongoingMiningJobs[minerIdentityHash];
		let hashAnswer = cryptoTools.sha256(minerWorkingBlock.dataHash + minerWorkingBlock.timestamp + nonce);
		
		if(hashAnswer == minerClaim && hashAnswer.startsWith('0'.repeat(this.currentDifficulty))) {
			// block is valid - add to chain
			minerWorkingBlock.nonce = nonce;
			minerWorkingBlock.hash = hashAnswer;
			
			this.addNewBlock(minerWorkingBlock);
			logger.info("Block accepted");
		} else {
			// @TODO reject the block and notify miner
			logger.error("Block rejected");
		}
	}
	
	addNewBlock(blockData) {
		this.blocks.push(blockData);
	}
	
	addNewTransaction(tranData) {
	}
};

let t = new Node(genesisBlock, startDifficulty);
let minerAddr = 'testAddr';
let test = t.getMiningJob(minerAddr);
let i = 0;
let target = '0'.repeat(startDifficulty);
while( true ) {
	let v = cryptoTools.sha256(test.dataHash + test.timestamp + i);
	logger.debug("I: " + i);
	logger.debug("V: " + v);
	if(v.startsWith(target)) {
		t.receiveMinerData(test.dataHash, i, v);
		break;
	}
	i++;
}