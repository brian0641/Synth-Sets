# Trade Signal Format

For version 0 of the *trade signal server*, trade signals are encoded as simple JSON objects. Initially, the trade signals are provided in the file: trade_signals.json.  Because the TokenSet trade signals tend to be infrequent, it is feasible to simply manually add the trade signals to the file.

Format of a trade signal in trade_signals.json:

Fields in a trade signal:
* **execution_time**: Date/Time string in ISO 8601 format, including time zone. The is the date at which the trade is to be executed (broadcast to the blockchain). The code "NOW" or "" is to be used to send the trade immediately.
* **trades**: List of trade_objects, where each trade_object includes a dictionary of {"from": synth_name_from, "to": synth_name_to, "percent": percent_of_from_synths}. Percent_of_from_synths is the portion of the balance of the from synth to include in the exchange.
* **name**: The name of the strategy being implemented.

Example trade_signal.json file:
```
[
  {
    "execution_time": "2020-01-12T14:10:53Z",
    "trades": [ {"from": "sUSD", "to": "sETH", "percent": 100} ]
    "name": "ETH20MACO"
  }
]
```
