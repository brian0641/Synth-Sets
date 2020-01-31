import web3, json, time

class TradeExecutor():
    """ Class to submit synthetix.exchange txes to the blockchain. 
    
    """    
    def __init__(self, pw3, synthetix_contract_address, signing_accounts, network, min_fee_rate, logger):
        """
        w3: A web3.Web3 instance 
        synthetix_contract_address: address of the synthetix contract
        signing_accounts: dictionary of address=> private key that are to be used when signing exchange transactions 
        network: "mainnet" or "kovan"
        """
        self.w3 = w3
        self.abi = json.load(open("../contracts/abi.json", "r"))
        self.synth_abi = json.load(open("./abis/synth_abi.json", "r"))
        self.log = logger
        
        self.synthetix_contract = self.w3.eth.contract(address = synthetix_contract_address,
                                                       abi = json.load(open("./abis/synthetix_abi.json", "r")))
        
        self.synths = {}  #synth_name => synth contract instance
        self.contracts = {}
        
        self.signing_accounts = signing_accounts
        self.min_fee_rate = min_fee_rate
        if network == "mainnet":
            self.chainId = 1
        elif network == "kovan":
            self.chainId = 1
        else:
            raise ValueError("Unknown network name")
        
        
    def executeOne(self, trade_signal, contract_address, contract_state, min_fee_rate = 0):
        """Call the trade method on a single contract.
        
        min_fee_rate: the minimum fee rate accepted by this server.
        
        Returns: iterable of the tx_hashes of the transactions. Returns [] if an error."""
        if not contract_address in self.contracts:
            self.contracts[contract_address] = self.w3.eth.contract(address = contract_address, abi = self.abi)
        k = self.contracts[contract_address]
        
        #Check that contract state info satisfies constraints
        if not contract_state['enableTrading']: 
            self.log("Trading is not enabled for the contract: {}".format(contract_address))
            return []
        if contract_state['feeRate'] < min_fee_rate: 
            self.log("Minimum fee rate of the contract is too low. Contract: {}".format(contract_address))
            return []   
        
        #Get current gas price limit that is allowed by the synthetix contract
        gpl = self.synthetix_contract.functions.gasPriceLimit().call()     
        
        if trade_signal['type'] == "type1":
            try:
                txn_hashes = self._executeType1(trade_signal, k, contract_state, gpl)
            except:
                self.log("Error executing Type1 trade signal: {}".format(trade_signal))
        elif trade_signal['type'] == "type2":
            try:
                txn_hashes = self._executeType2(trade_signal, k)
            except:
                self.log("Error executing Type2 trade signal: {}".format(trade_signal))            
        elif trade_signal['type'] == "type3":
            try:
                txn_hashes = self._executeType3(trade_signal, k, contract_state, gpl)
            except:
                self.log("Error executing Type3 trade signal: {}".format(trade_signal))            
        else:
            self.log('Trade signal *type* field was not recognized.')
            txn_hashes = []
        return txn_hashes
    
    def _executeType1(self, trade_signal, k, contract_state, gpl):
        all_synths = set()
        for t in trade_signal["params"]["trades"]:
            all_synths.add(t['from'])
            
        balances = self.getBalances(k, all_synths)
        
        txn_hashes = []
        for t in trade_signal['params']['trades']:
            balance = balances.get(t['from'])
            if balance != None and balance > 0: 
                amt = int(balance * t['percent'] / 100)
                amt = min(balance, amt)
            
                src_curr_key = self._nameToKey(t['from'])
                dst_curr_key = self._nameToKey(t['to'])
                
                #Build and send transaction
                trader_address = contract_state['trader']
                nonce = self.w3.eth.getTransactionCount(trader_address)  
                
                #Build a transaction that invokes this contract's function, called transfer
                options = {'chainId': self.chainId, 'gas': 500000, 'gasPrice': gpl, 'nonce': nonce}
                
                txn = k.functions.trade(src_curr_key, amt, dst_curr_key, self.min_fee_rate).buildTransaction(options)
                
                signed_txn = self.w3.eth.account.sign_transaction(txn, private_key=self.signing_accounts[trader_address])
                
                self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)  
                txn_hash = self.w3.toHex(self.w3.keccak(signed_txn.rawTransaction))   
                txn_hashes.append(txn_hash)
                
        return txn_hashes
    
    def _executeType2(self, trade_signal, k):
        #TODO - this trade type requires the current exchange rates
        raise NotImplementedError
        #all_synths = set()
        #for synth in trade_signal["params"]["synths"]:
            #all_synths.add(t['from'])
            
        #balances = self.getBalances(k, all_synths)
        
        #balance_total = sum(list(balances.values()))
        #weight_total = float(sum(trade_signal["params"]["weights"]))
        
        #desired_balances = {}
        #for synth in trade_signal["params"]["synths"]:
            #desired_balances[synth] = 
        
    def _executeType3(self, trade_signal, k, contract_state, gpl):
        all_synths = set()
        for arr in trade_signal["params"]["pairs"]:
            all_synths.add(arr[0])
            all_synths.add(arr[1])
            
        balances = self.getBalances(k, all_synths)
        
        txn_hashes = []
        for arr in trade_signal["params"]["pairs"]:
            synth1 = arr[0]; synth2 = arr[1]
            if balances[synth1] > balances[synth2]:
                from_synth = synth1
                to_synth = synth2
            else:
                from_synth = synth2
                to_synth = synth1
                
            if balances[from_synth] != None and balances[from_synth] > 0: 
                amt = int(balance)
            
                src_curr_key = self._nameToKey(from_synth)
                dst_curr_key = self._nameToKey(to_synth)
                
                #Build and send transaction
                trader_address = contract_state['trader']
                nonce = self.w3.eth.getTransactionCount(trader_address)  
                
                #Build a transaction that invokes this contract's function, called transfer
                options = {'chainId': self.chainId, 'gas': 500000, 'gasPrice': gpl, 'nonce': nonce}
                
                txn = k.functions.trade(src_curr_key, amt, dst_curr_key, self.min_fee_rate).buildTransaction(options)
                
                signed_txn = self.w3.eth.account.sign_transaction(txn, private_key=self.signing_accounts[trader_address])
                
                self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)  
                txn_hash = self.w3.toHex(self.w3.keccak(signed_txn.rawTransaction))   
                txn_hashes.append(txn_hash)
                
        return txn_hashes
    
    def getBalances(self, contract_instance, synths):
        """
        synths: iterable of the synth names for which the balances is to be retrieved.
        contract_instance: web3 instance of the tradeProxy contract that has the synths
        
        Return: dictionary of {"synth_name": balance}, where balances are in wei
        
        """
        d = {}
        for synth in synths:
            synth_k = self.synths.get(synth)
            if not synth_k:
                synth_k = self.synths[synth] = self._instantiate_synth(synth)
                self.synths[synth] = synth_k
            balance = synth_k.functions.balanceOf(contract_instance.address).call()
            d[synth] = balance
        return d
                
    def _instantiate_synth(self, synth_name):
        currKey = self._nameToKey(synth_name)
        address = self.synthetix_contract.functions.synths(currKey).call()
        k = self.w3.eth.contract(address = address, abi = self.synth_abi)
        return k
    
    def _currKeyToString(self, key):
        chars = [key[i:i+2] for i in range(0, len(key), 2)][1:]
        s = [chr(int(v,16)) for v in chars if int(v,16) != 0]
        return "".join(s)
    
    def _nameToKey(self, synth_name):
        """Returns a 32 byte hex string ("0x54...") representing the input. """
        s = ""
        for i in range(32):
            if i < len(synth_name):
                s += hex(ord(synth_name[i]))[2:]
            else:
                s += "00"
        return "0x" + s    
            
if __name__ == "__main__":
    #url = """ <A URL GOES HERE>"""
    #provider = web3.Web3.HTTPProvider(url)
    
    url_kovan = """KOVAN_URL"""
    provider = web3.Web3.HTTPProvider(url_kovan)
    
    w3 = web3.Web3(provider)
    print("Connected:", w3.isConnected())
    
    #abi = json.load(open("../contracts/abi.json", "r"))
    #k_address = "0x7C34D8bB789C354fD7Ed1B32466cF8c84F360602"
    
    synthetix_contract_address = "0x22f1ba6dB6ca0A065e1b7EAe6FC22b7E675310EF"
    
    address = "0x4C9DEA94C1A1e81bB79ccC5C301CFeffeA8ADDa8"  #address of trader
    p_key = "KEY"
    
    ex = TradeExecutor(provider, synthetix_contract_address, {address:p_key})
    ex._instantiate_synth("sETH")
    
    myContractAddress = "0xC726d5D3A5037D7057dd307852240ae0AcC19aC6"
    k = w3.eth.contract(address = myContractAddress,
                             abi =  json.load(open("../contracts/abi.json", "r")))    
    balances = ex.getBalances(k, ["sETH"])
    
    import ContractMonitor
    qq = ContractMonitor.ContractMonitor(provider, [myContractAddress])
    k_state = qq.getContractState(myContractAddress)
    
    time.sleep(10)
    
    _trades = [ {"from": "sETH", "to": "sUSD", "percent": 50}, {"from": "sETH", "to": "sUSD", "percent": 25} ]
    signal =  {"execution_time": "2020-01-12T14:10:53Z", "trades": _trades, "name": "ETH20MACO"}
    
    ex.executeOne(signal, myContractAddress, k_state)
    
    