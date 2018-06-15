const cryptoTools = require("./utilities/CommonCryptoTools");

module.exports = class Block {
	constructor(
		index,
		timestamp,
		transactions,
		nonce,
		prevHash,
		difficulty,
		minedBy,
		dataHash,
		hash
	)
	{
		this.index = index;
		this.transactions = transactions;
		this.difficulty = difficulty;
		this.prevHash = prevHash;
		this.minedBy = minedBy;
		this.dataHash = dataHash;
		
		// calculated in miner
		this.nonce = nonce;
		this.timestamp = timestamp;
		this.hash = hash;
		
		if (this.dataHash === undefined) {
			this.createDataHash();
		}
	}
	
	createDataHash() {
		let blockData = {
			'index': this.index,
			'transactions': this.transactions.map(t => Object({
				'from': t.from,
				'to': t.to,
				'value': t.value,
				'fee': t.fee,
				'timestamp': t.timestamp,
				'data': t.data,
				'senderPubKey': t.senderPubKey,
				'transactionDataHash': t.transactionDataHash,
				'senderSignature': t.senderSignature
			})),
			'difficulty': this.difficulty,
			'prevHash': this.prevHash,
			'minedBy': this.minedBy
		};
		let blockDataJSON = JSON.stringify(blockData);
		this.dataHash = cryptoTools.sha256(blockDataJSON);
	}
};