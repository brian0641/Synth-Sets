
import web3, json, time, datetime,sys, zmq
import tokenSet_config as cfg


def log(s):
    dt = datetime.datetime.now().strftime("%m-%d %H:%M:%S")
    print(dt + " " + s)
    with open("logger.log" , 'a') as f:
        f.write(dt + " " + s + '\n')   

def fetchActiveSetTokens(core_k, w3, monitored_symbols):
    setToken_abi = json.load(open("setToken-contract-abi.json", "r"))
    setToken_addresses = core_k.functions.setTokens().call()
    active_setTokens = {}
    for addr in setToken_addresses:
        r = core_k.functions.validSets(addr).call()
        if r:
            st_k = w3.eth.contract(address = addr, abi = setToken_abi)
            symbol = st_k.functions.symbol().call()
            if symbol in monitored_symbols:
                d = {'symbol': symbol, 'addr': addr, 'contract': st_k}
                active_setTokens[symbol] = d
    return active_setTokens

def fetchRebalancing(active_setTokens):
    """Returns a set of the symbols that have a state == 2 (rebalancing)"""
    r = set()
    for _symbol, d in active_setTokens.items():
        state = d['contract'].functions.rebalanceState().call()
        if state == 2:
            r.add(d['symbol'])
    return r

def main():
    log("Starting main loop of tokenSet signal generator .. scanning for set rebalancing.")
    
    #Initialization stuff
    monitored_symbols = list(cfg.tokenSet_symbols.keys())
    log("Symbols that are being monitored are: {}".format(monitored_symbols))
    abi_core = json.load(open("abi_core.json", "r"))
    provider = web3.Web3.HTTPProvider(cfg.getConnectionUrl())
    w3 = web3.Web3(provider)
    core_k = w3.eth.contract(address = cfg.getCoreAddress(), abi = abi_core)  
    
    #zmq socket initialization
    context = zmq.Context()
    sender = context.socket(zmq.PUSH)
    sender.connect(cfg.zmqPushSocket)
    
    #State variables
    rebalancing_tokens = set()
    active_setTokens = {}
    last_active_tokenSet_fetch = 0
    ONE_HOUR = 60 * 60
    
    #Main loop
    while True:
        
        #For each monitored setToken, build a dictionary of the fields:
        # {symbol, addr, contract}. Rebuild active sets no more than once and hour and only
        #if there are no currently rebalancing sets.
        if time.time() - last_active_tokenSet_fetch > ONE_HOUR and len(rebalancing_tokens) == 0:
            active_setTokens = fetchActiveSetTokens(core_k, w3, monitored_symbols) 
            last_active_tokenSet_fetch = time.time()
            
        # Get set of the active tokens that are rebalancing
        _rebalancing_tokens = fetchRebalancing(active_setTokens)   
        new_rebalancing = _rebalancing_tokens - rebalancing_tokens
        
        
        for symbol in new_rebalancing:
            k = active_setTokens[symbol]['contract']
            remain_shares = k.functions.biddingParameters().call()[1]
            active_setTokens[symbol]['initial_remaining'] = remain_shares
            rebalancing_tokens.add(symbol)
            log("Rebalancing beginning detected for symbol: " + symbol)
        
        remove_tokens = set()
        for symbol in rebalancing_tokens:
            k = active_setTokens[symbol]['contract']
            remain_shares = k.functions.biddingParameters().call()[1]
            if remain_shares <= active_setTokens[symbol]['initial_remaining']/2:
                #generate signal and send over the zeroMQ channel. 
                signal = cfg.tokenSet_symbols[symbol]
                signal['execution_time'] = 'NOW'
                signal['name'] = symbol
                sender.send(json.dumps(signal))
                log("Rebalance Execution detected for symbol: " + symbol)
                remove_tokens.add(symbol)
        rebalancing_tokens = rebalancing_tokens - remove_tokens
        
        time.sleep(60)
    
if __name__ == "__main__":
    try:
        main()
    except:
        log("Unhandled error - SHUTTING DOWN: {}".format(sys.exc_info()[0]))
    
