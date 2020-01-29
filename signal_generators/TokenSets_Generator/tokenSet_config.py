#
# Configuration file for tokenSet_signal_generator.py
#

zmqPushSocket = "tcp://localhost:6237"

#
#Ethereum network connection 
#
# network = "mainnet" or "kovan"
network = "mainnet"
def getConnectionUrl():
    if network == "kovan":
        return  """KOVAN NODE URL GOES HERE"""
    elif network == "mainnet":
        return """https://grossly-becoming-sailfish.quiknode.io/6e1c4338-e2be-48ae-be0e-aa7dba60c684/OhIG80rMIgd9CHXQstdQTg==/"""
def getCoreAddress():
    """address of the tokenSet 'core' module"""
    if network == "kovan":
        return  "ADDRESS_GOES_HERE"
    elif network == "mainnet":
        return "0xf55186CC537E7067EA616F2aaE007b4427a120C8"
    
#
# The Supported tokenSet symbols (dictionary)
# The keys are the tokenSet symbol. The values are a partial trade signal 
# appropriate for the strategy.
#
tokenSet_symbols = \
{
    "ETH20SMACO" : {"type": "type3", "params" : { "pairs": [["sUSD", "sETH"]]}},
    "ETH26EMACO" : {"type": "type3", "params" : { "pairs": [["sUSD", "sETH"]]}},
    "ETH12EMACO" : {"type": "type3", "params" : { "pairs": [["sUSD", "sETH"]]}},
    "ETHBTCRSI" : {"type": "type3", "params" : { "pairs": [["sBTC", "sETH"]]}},
    "ETHRSI6040" : {"type": "type3", "params" : { "pairs": [["sUSD", "sETH"]]}},
    "BTCETH7525" : {"type": "type2", "params" : { "synths": ["sBTC", "sETH"], "weights": [75, 25]} }
}