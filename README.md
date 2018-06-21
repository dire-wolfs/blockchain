# blockchain practical project


## wallet

`GET /`                     - UI

`GET /account/<pkey>'`      - sign in with a private key

`GET /account`              - view account information

`POST /account`             - create new account (address)

`DELETE /account`           - sign out of account

`POST /transactions/sign`   - sign/create a transaction with current account and return it

`POST /transactions/verify` - verify signed transaction

`GET /balance`              - show account balance

Talks to the `node` to get the transactions and calculate a balance.
Accounts are stored by IP of client. 

 
## faucet

`GET /faucet/<account_id>`  - send 5 coins to account


Talks to `wallet` to create signed transaction and sends it to the `node` to include in the next block. 

## miner

Talks to `node` as asks for new job and then mines it.

## node

Should include block explorer.

TODO:

`GET /transactions` - Get all transactions so far (perhaps should be blocks and iterate over blocks)

`GET /blocks/last-block` - Get the last block on the chain

`GET /mining/get-mining-job/<address>` - Get mining job, ready to mine (block_data_hash, difficulty, etc.)

`POST /mining/submit-mined-block` - Submit minded job (nonce, hash, timestamp)

`POST /transactions/send` - Add/Create new transaction for the next block