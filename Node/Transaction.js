const cryptoTools = require("./utilities/CommonCryptoTools");

module.exports = class Transaction {
	constructor(
		from,
		to,
		value,
		fee,
		timestamp,
		data,
		senderPubKey,
		transactionDataHash,
		senderSignature,
		minedInBlockIndex,
		transferSuccessful
	)
	{
		this.from = from;
		this.to = to;
		this.value = value;
		this.fee = fee;
		this.timestamp = timestamp;
		this.data = data;
		this.senderPubKey = senderPubKey;
		this.transactionDataHash = transactionDataHash;
		this.senderSignature = senderSignature;
		
		if (this.transactionDataHash === undefined) {
			this.calculateDataHash();
		}
	}
	
	calculateDataHash() {
		let tranData = {
			'from': this.from,
			'to': this.to,
			'value': this.value,
			'fee': this.fee,
			'timestamp': this.timestamp,
			'data': this.data,
			'senderPubKey': this.senderPubKey
		};
		let tranDataJSON = JSON.stringify(tranData);
		this.transactionDataHash = cryptoTools.sha256(tranDataJSON);
	}
	
	sign(privateKey) {
		this.senderSignature = cryptoTools.signData( his.transactionDataHash, privateKey);
	}
	
	verifySignature() {
		return cryptoTools.verifySignature(this.transactionDataHash, this.senderPubKey, this.senderSignature);
	}
};