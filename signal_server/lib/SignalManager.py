import time, json
import dateutil.parser, pytz, datetime, os.path



class SignalManager():
    """ Class to manage and provide the reading of trade signals."""
    def __init__(self, fn_signals, logger):
        self.signals = []  #list of pending trade signals
        self.signals_last_read_time = 0   #timestamp of last read 
        
        self.fn_signals = fn_signals
        
        self.signals = self.readSignalFile()
        self.signals_last_read_time = os.path.getmtime(self.fn_signals) 
        
        self.log = logger
        
    def readSignalFile(self):
        """ Reads the signal file. 
        Returns:  an iterable of all the signals in the signal file.
        """
        signals = []
        try:
            signals = json.load(open(self.fn_signals, "r"))
        except:
            raise ValueError("Error reading the signal file.")
        return signals
        
    def removeSignalsAndWriteFile(self, signals):
        """
        Remove signals from the disk stoarge. This method would typically be called when a trade signal 
        was successfully processed. Signals are matched to one
        another by using the "execution time" and "name" field as a key.
        
        signals: iterable of trade signals that are to be removed from the signal file. 
        
        Returns True if successful
        """
        out_signals = [] 
        
        if not signals:   #exit if nothing was passed
            return True 
        
        #filter the signals on disk to remove those in signals
        set_signals = set( [(s['execution_time'], s['name']) for s in signals] )
        try:
            for signal in self.readSignalFile():
                set_signal = set([(signal['execution_time'], signal['name'])])
                if not (len(set_signals.difference(set_signal)) < len(set_signals)):
                    out_signals.append(signal)
             
            self.signals = out_signals
            with open(self.fn_signals, "w") as write_file:
                json.dump(out_signals, write_file)                
            return True
        except:
            return False
        
    def triggeredSignals(self, max_behind_mins):
        """Returns a list of signals that have been triggered based on the execution_time field.
        
        max_behind_mins: if the scheduled execution time for a signal is more than this number of minutes in the 
                         past, the signal is not executed.
        """
        triggered = []; errors = []
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
        return triggered, errors
        
        
    def fileUpdated(self):
        """Checks self.fn_signals to determine if file was updated. If so,
        read in and the new version of the signals from the file. 
        
        Return True if a new version was detected. Otherwise False.
        """
        if os.path.getmtime(self.fn_signals) > self.signals_last_read_time:
            self.signals_last_read_time= os.path.getmtime(self.fn_signals)
            self.signals = self.readSignalFile()
            return True
        return False
        
    
if __name__ == "__main__":
    pass