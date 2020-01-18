import web3, json, time, os, sys

class ContractMonitor():
    """ Class to monitor the state of tradeProxy.sol contracts. 
    
        The run method should be called to start the monitoring loop.
        
        The state for each monitored contract is stored in a dictionary. For example:
        {
         'enableTrading': True,
         'feeRate': 10000,
         'minMinsBtwTrades': 5,
         'owner': '0xB75Af109Ca1A6dB7c6B708E1292ee8fCc5b0B941',
         'trader': '0x4C9DEA94C1A1e81bB79ccC5C301CFeffeA8ADDa8',
         'tradingStrategyLabel': 'EMA20CO'
        }        
    """    
    def __init__(self, provider, contracts_to_monitor_fn, logger):
        """
        provider: A web3.Web3 provider instance (e.g., provider = web3.Web3.HTTPProvider(url))
        initial_addresses_to_monitor: List of contract addresses.
        """
        self.w3 = web3.Web3(provider)
        self.abi = json.load(open("../contracts/abi.json", "r"))
        
        self.log = logger
                
        self.contract_state = {}  #address => state dictionary
        self.contracts = {}       #address => w3.eth.contract instance
        
        initial_addresses_to_monitor = json.load(open(contracts_to_monitor_fn, "r"))
        
        self.contracts_to_monitor_fn = contracts_to_monitor_fn
        self.contracts_file_last_modify = os.path.getmtime(self.contracts_to_monitor_fn) 
        
        for _address in initial_addresses_to_monitor:
            try:
                self._initializeState(_address)
            except:
                self.log("Error initializing contract: {}. Skipping. Msg: {}".format(_address, sys.exc_info()[0])) 
        
    def getContractState(self, address):
        return self.contract_state.get(address)
    
    def getAllMonitoredAddresses(self):
        """
        Returns the addresses of all of the monitored contracts.
        """
        return list(self.contracts.keys())
    
    def getAddressesThatMatchLabel(self, label):
        """
        Returns a list of all the contract address in which the state field 'tradingStrategyLabel' matches
        the input label.
        """
        result = []
        for address, state in self.contract_state.items():
            if state['tradingStrategyLabel'] == label:
                result.append(address)
        return result
        
    
    def addContract(self, address):
        """
        Adds a new contract to monitor.
        """
        try:
            self._initializeState(address)
        except:
            self.log("Error initializing contract: {}. Skipping. Msg: {}".format(_address, sys.exc_info()[0]))         
    
    def run(self):
        UPDATE_PERIOD_MINUTES = 5
        last_update_ts = 0
        while 1:
            # Periodically poll contract state info
            if time.time() > last_update_ts + 60 * UPDATE_PERIOD_MINUTES:
                for _address in self.contracts.keys():
                    self.updateState(_address) 
                last_update_ts = time.time()
                
            #check whether the file containing the addresses to monitor has been updated, add
            # or delete from self.contracts and self.contract_state as appropriate
            if os.path.getmtime(self.contracts_to_monitor_fn) > self.contracts_file_last_modify:
                self.contracts_file_last_modify = os.path.getmtime(self.contracts_to_monitor_fn) 
                addresses = set(json.load(open(self.contracts_to_monitor_fn, "r")))
                existing_add = set(self.contracts.keys())
                new_addresses = addresses.difference(existing_add)
                delete_addresses = existing_add.difference(addresses)
                for _address in new_addresses:
                    self._initializeState(_address)
                for _address in delete_addresses:
                    del self.contracts[_address]
                    del self.contract_state[_address]
            
            time.sleep(10)
    
    def updateState(self, contract_address):
        if contract_address in self.contracts:
            k = self.contracts[contract_address]
            d = {}
            d['enableTrading'] = k.functions.enableTrading().call()
            d['feeRate'] = k.functions.feeRate().call()
            d['minMinsBtwTrades'] = k.functions.minMinsBtwTrades().call()
            d['trader'] = k.functions.trader().call()
            d['tradingStrategyLabel'] = k.functions.tradingStrategyLabel().call() 
            
            self.contract_state[contract_address].update(d)
            
    def _initializeState(self, contract_address):
        try:
            k = self.w3.eth.contract(address = contract_address, abi = self.abi)
        except:
            return None
        d = {}
        d['enableTrading'] = k.functions.enableTrading().call()
        d['feeRate'] = k.functions.feeRate().call()
        d['minMinsBtwTrades'] = k.functions.minMinsBtwTrades().call()
        d['trader'] = k.functions.trader().call()
        d['owner'] = k.functions.owner().call()
        d['tradingStrategyLabel'] = k.functions.tradingStrategyLabel().call()        
        
        self.contract_state[contract_address] = d    
        self.contracts[contract_address] = k
        
    
if __name__ == "__main__":
    #url = """ <A URL GOES HERE>"""
    #provider = web3.Web3.HTTPProvider(url)
    
    url_kovan = """https://kovan.infura.io/v3/b55025fe413948fd80744f09d4688f61"""
    provider = web3.Web3.HTTPProvider(url_kovan)
    
    w3 = web3.Web3(provider)
    print("Connected:", w3.isConnected())
    
    abi = json.load(open("../contracts/abi.json", "r"))
    k_address = "0x7C34D8bB789C354fD7Ed1B32466cF8c84F360602"
    k = w3.eth.contract(address = k_address, abi = abi)
    
    print(k.address)
    
    print(k.functions.enableTrading().call())
    
    
    #call initial state of contract
    d = {}
    d['enableTrading'] = k.functions.enableTrading().call()
    d['feeRate'] = k.functions.feeRate().call()
    d['minMinsBtwTrades'] = k.functions.minMinsBtwTrades().call()
    d['owner'] = k.functions.owner().call()
    d['trader'] = k.functions.trader().call()
    d['tradingStrategyLabel'] = k.functions.tradingStrategyLabel().call()
    
    
    import pprint
    pprint.pprint(d)
    
    
    #subscribe to events
    
    
    
    
    
        
