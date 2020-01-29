#
# Configuration file for trade_signal_server
#

#
# Configure channels over which trade signals are received.
# zmqPullSocket   => enter the socket info; set to None if not used.
zmqPullSocket = "tcp://*:6237"

#The contracts (addresses) that are to be monitored are stored in a json file
contracts_to_monitor_fn = "contracts_to_monitor.json"

#The possible accounts for the Trader. Dictionary of address => priv_key
signing_accounts = {"ADDRESS_GOES_HERE":"PRIV_KEY"}

#the minimum fee rate that is accepted by the server (in units of basis points * 10000; e.g. 0.02% fee rate = 200)
MIN_FEE_RATE = 0

#if the scheduled execution time for a signal is more than this number of minutes 
#in the  past, the signal is not executed.
MAX_MINS_BEHIND= 5

#
#Ethereum network connection 
#
# network = "mainnet" or "kovan"
network = "mainnet"
def getConnectionUrl():
    if network == "kovan":
        return  """KOVAN NODE URL GOES HERE"""
    elif network == "mainnet":
        return """MAIN_NODE_URL_GOES_HERE"""
def getSynthetixAddress():
    """Address of the synthetix contract"""
    if network == "kovan":
        return  "0x22f1ba6dB6ca0A065e1b7EAe6FC22b7E675310EF"
    elif network == "mainnet":
        return "0xC011A72400E58ecD99Ee497CF89E3775d4bd732F"    
    
