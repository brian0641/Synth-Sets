""" Script for sending manually generated signals to the signal_server. 

    Launch using something like: python3 manual.py signal_file.json
    The script will read the trade signals in "signal_file.json" and send to the signal server. If no file name is given,
    "signals.json" will be used as the default name.
    
    See "trade_signal_format.md" for a description of the signal format.
    
    The json encoded file should include a single signal (dictionary) or a list of signals.
    
    An optional second argument can be used to specify the zmq socket (default is "tcp://localhost:6237")
"""

FN = "signals.json"
ZMQ_PUSH_SOCKET = "tcp://localhost:6237"

import sys, json, zmq, pprint

if __name__ == "__main__":
    if len(sys.argv) > 1:
        FN = sys.argv[1]
        
    if len(sys.argv) > 2:
        ZMQ_PUSH_SOCKET = sys.argv[2]        
        
    try:   
        signals = json.load(open(FN, "r"))
    except json.decoder.JSONDecodeError:
        print("Error Decoding the json signal file")
        sys.exit(1)
    
    if type(signals) == dict:
        signals = [signals]
        
    context = zmq.Context()
    sender = context.socket(zmq.PUSH)
    sender.connect(ZMQ_PUSH_SOCKET) 

    i = 0
    for s in signals:
        sender.send_string(json.dumps(s))
        print("Signal sent to trade_signal_server")
        pprint.pprint(s)
        print()
        i += 1
    print("Finished transmitting signals. Number transmitted: {}".format(i))
 