import web3, json
def checkTxHashes(pending_tx_hashes, w3, log):
    """Fetches the status of the tx_hashes.
    
    Return: a tuple of still_pending, completed iterable.
    """
    keys = ['blockHash', 'blockNumber', 'contractAddress', 'cumulativeGasUsed', 'from', 'gasUsed', 'status', 'to', 'transactionHash', 'transactionIndex']
    still_pending = []; completed = []
    for tx_hash, _signal, _ts in pending_tx_hashes:
        try:
            r = w3.eth.getTransactionReceipt(tx_hash)
            d = {k:r[k] for k in keys}
            d['blockHash'] = d['blockHash'].hex()
            d['transactionHash'] = d['transactionHash'].hex()
            if d['status'] == 1:
                log("Success TX Included in Block: " + json.dumps(d))  
            else:
                log("Failed TX Included in Block: " + json.dumps(d))              
            completed.append((tx_hash, _signal, _ts))
        except web3.exceptions.TransactionNotFound:   #tx not mined yet
            still_pending.append((tx_hash, _signal, _ts))

    return still_pending, completed