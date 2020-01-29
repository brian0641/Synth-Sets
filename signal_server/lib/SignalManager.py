import time, json, threading
import dateutil.parser, pytz, datetime, os.path

class SignalManager():
    """ Class to manage and provide the reading of trade signals."""
    def __init__(self, cfg, logger):
        self.signals = []  #list of pending trade signals
        
        if cfg.zmqPullSocket:
            import zmq
            context = zmq.Context()
            self.receiver = context.socket(zmq.PULL)
            self.receiver.bind(cfg.zmqPullSocket) 
            
            t = threading.Thread(target=self._zmqReceive) #start thread to receive zmq signals
            t.start()   
        else:
            self.log("zmq socket was not configured. Signals will not be received by the trade_signal_server.")
        
        self.log = logger
        
    def triggeredSignals(self, max_behind_mins):
        """Returns a list of signals that have been triggered based on the execution_time field. Triggered 
        signals are removed from self.signals.
        
        max_behind_mins: if the scheduled execution time for a signal is more than this number of minutes in the 
                         past, the signal is not executed.
        """
        triggered = []; errors = []; _signals = []
        for s in self.signals:
            if s['execution_time'] == "NOW" or s['execution_time'] == "":
                triggered.append(s)
            else:
                signal_dt = dateutil.parser.parse(s['execution_time'])
                if datetime.datetime.now(pytz.timezone("utc")) - datetime.timedelta(minutes = max_behind_mins) > signal_dt:
                    self.log("Trade signal execution time is too far in the past. {}".format(s))
                    errors.append(s)
                elif datetime.datetime.now(pytz.timezone("utc")) > signal_dt:
                    triggered.append(s)
                else:
                    _signals.append(s)
        self.signals = _signals
        return triggered, errors
        
    def _zmqReceive(self):
        while 1:
            s = self.receiver.recv()
            signal = json.loads(s)
            if 'execution_time' in signal and 'params' in signal and \
            'name' in signal and 'type' in signal:    #check valid signal
                self.signals.append(signal)
            else:
                self.log("Invalid trade signal received via zmq")
            time.sleep(1)
        
    
if __name__ == "__main__":
    pass