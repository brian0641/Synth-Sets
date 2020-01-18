
import time, json, web3, threading, datetime, sys
import lib.ContractMonitor, lib.SignalManager, lib.TradeExecutor, lib.Utils
import server_config as cfg


def log(s):
    dt = datetime.datetime.now().strftime("%m-%d %H:%M:%S")
    print(dt + " " + s)
    with open("logger.log" , 'a') as f:
        f.write(dt + " " + s + '\n')   


def main():
    # SignalManger manages the inputting of trade_signals. Currently a simple file system is used communicate the trade signals.
    sm = lib.SignalManager.SignalManager(cfg.trade_signals_fn, log)
    
    # ContractMonitor monitors the state of tradeProxy.sol contracts (e.g., trading enabled, trade strategy selected, etc.). 
    provider = web3.Web3.HTTPProvider(cfg.getConnectionUrl())
    w3 = web3.Web3(provider)
    cm = lib.ContractMonitor.ContractMonitor(provider, cfg.contracts_to_monitor_fn, log)
    threading.Thread(target=cm.run).start() #start thread to periodically fetch contract state info from the blockchain
    
    # TradeExecutor submits the trade txes to the blockchain. 
    te = lib.TradeExecutor.TradeExecutor(provider, cfg.getSynthetixAddress(), cfg.signing_accounts, 
                                         cfg.network, cfg.MIN_FEE_RATE, log)
    
    pending_tx_hashes = []
    
    while True:
        if sm.fileUpdated():
            log("Signal file was updated.")
        
        triggered_signals, error_signals = sm.triggeredSignals(cfg.MAX_MINS_BEHIND)
        sm.removeSignalsAndWriteFile(error_signals)
        
        if triggered_signals:
            for signal in triggered_signals:
                addresses = cm.getAddressesThatMatchLabel(signal['name'])
                log("A signal was triggered: {}. Matching addresses: {}".format(signal['name'], addresses))
                for contract_address in addresses:
                    tx_hashes = te.executeOne(signal, contract_address, cm.getContractState(contract_address), cfg.MIN_FEE_RATE)
                    for tx_hash in tx_hashes:
                        log("Initial TX receipt:" + str(w3.eth.getTransaction(tx_hash)))                
                    log("Signal submitted. Tx hash(es): {}. Signal:{}".format(tx_hashes, signal))
                    tx_hashes = [(v, signal, time.time()) for v in tx_hashes]
                    pending_tx_hashes.extend(tx_hashes)
            sm.removeSignalsAndWriteFile(triggered_signals)  #remove the process signals from the input signal queue
                    
        #Check status of pending tx hashes
        pending_tx_hashes, _completed = lib.Utils.checkTxHashes(pending_tx_hashes, w3)
        
        time.sleep(5)
    
if __name__ == "__main__":
    try:
        main()
    except:
        log("Unhandled error - SHUTTING DOWN: {}".format(sys.exc_info()[0]))
    
