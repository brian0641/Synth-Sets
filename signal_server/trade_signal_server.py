
import time



class ManageSignals():
    """ Class to manage and provide the reading of trade signals and to keep an 
    up-to-date list of contract addresses that are to be monitored."""
    def __init__(self, fn_signals, fn_addresses):
        self.signals = []  #list of upcoming trade signals
        self.addresses = [] #list of current addresses to monitor.
        self.signals_last_read_TS = 0   #timestamp of last read 
        self.addresses_last_read_TS = 0  
        
        self.fn_signals = fn_signals
        self.fn_addresses = fn_addresses
        
        #TODO - initial read
        
    def update(self):
        """Checks self.fn_signals and self.fn_addresses to determine if file was updated. If so,
        read in the and add to self.signals and self.addresses, as appropriate. 
        
        Any signals that were previously registered as being executed are deleted from self.fn_signals.
        
        Returns a list of newly detected trade_signals and addresses
        """
        raise NotImplementedError
    
        new_trade_signals, new_addresses = [], []
    
        return new_trade_signals, new_addresses
    
    def registerSignalExecution(self, trade_signal):
        """Register a trade signal as being executed."""
        pass
    
    def _readFiles(self):
        pass 
    

        
        
    

state = ManageSignals("trade_signals.json", "addresses.json")

contract_state = 


while True:
    
    #check if config files have changed on disk
    new_trade_signals, new_addresses = state.update()
    
    
    
    
    
    time.sleep(5)
    