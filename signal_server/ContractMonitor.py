import web3, json, time

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
    def __init__(self, provider, initial_addresses_to_monitor):
        """
        provider: A web3.Web3 provider instance (e.g., provider = web3.Web3.HTTPProvider(url))
        initial_addresses_to_monitor: List of contract addresses.
        """
        self.address = initial_addresses_to_monitor
        self.w3 = web3.Web3(provider)
        self.abi = json.load(open("../contracts/abi.json", "r"))
        
        
        self.contract_state = {}  #address => state dictionary
        self.contracts = {}       #address => w3.eth.contract instance
        
        for _address in initial_addresses_to_monitor:
            self._initializeState(_address)
        
    def getContractState(self, address):
        return self.contract_state.get(address)
    
    def getAllMonitoredAddresses(self):
        """
        Returns the addresses of all of the monitored contracts.
        """
        return list(self.contracts.keys())
    
    def addContract(self, address):
        """
        Adds a new contract to monitor.
        """
        self._initializeState(address)
    
    def run(self):
        UPDATE_PERIOD_MINUTES = 5
        last_update_ts = 0
        while 1:
            if time.time() > last_update_ts + 60 * UPDATE_PERIOD_MINUTES:
                for _address in self.contracts.keys():
                    self.updateState(_address) 
                last_update_ts = time.time()
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
            self.contracts[contract_address] = self.w3.eth.contract(address = contract_address, abi = self.abi)
        except:
            return None
        k = self.contracts[contract_address]
        d = {}
        d['enableTrading'] = k.functions.enableTrading().call()
        d['feeRate'] = k.functions.feeRate().call()
        d['minMinsBtwTrades'] = k.functions.minMinsBtwTrades().call()
        d['trader'] = k.functions.trader().call()
        d['owner'] = k.functions.owner().call()
        d['tradingStrategyLabel'] = k.functions.tradingStrategyLabel().call()        
        
        self.contract_state[contract_address] = d        
        
    
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
    
    
    
    
    
        
