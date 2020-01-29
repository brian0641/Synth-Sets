# Signal Overview

Trade signals are provided, from *signal generators*, to the *signal server*. The *signal server* is the process that handles submitting of the signals to the blockchain.

# Supported Channels

One trade submission channel is currently supported for communicating the trade signals between a *signal generator* and the *signal server*.     
*  A ZeroMQ channel (socket-based) can be used in which one or more *signal generators* push signals to a *signal server*. The ZeroMQ PUSH-PULL socket is used (default port 6237).

The *signal server* configuration file can be edited to indicate what channels are to be used. Default is to use both.


# Trade Signal Format

Trade signals are encoded as simple JSON objects. Each trade signal must include a *type* field. The supported types of trade signals include the following.

All trade signals include the fields:
* **type** The type of the trade signal (e.g., "type1", "type2", etc.)
* **name** The name/symbol of the strategy being implemented. For example, the name field might be "ETH20SMACO", which indicates the the *signal server* is to implement this trade for all smart contracts that are following this strategy.
* **execution_time**: Date/Time string in ISO 8601 format, including time zone. The is the date at which the trade is to be executed (broadcast to the blockchain). The code "NOW" or "" is to be used to send the trade immediately.
* **params** An object that includes the parameters specific to the trade signal type.

### type1 Trade Signal

Trade signal that directs an exchange from one particular synth type to another synth type.

The *params* field should include a "trades" list of {from, to, percent} values, where *from* is the source synth, *to* is the destination synth, and *perent* is the percentage of the from synth that is to be traded.

An example type1 signal exchanging all sUSD to sETH:
```
  {
    "execution_time": "2020-01-12T14:10:53Z",
    "params": {"trades": [ {"from": "sUSD", "to": "sETH", "percent": 100} ]},
    "name": "ETH20MACO",
    "type": "type1"
  }
```

### type2 Trade Signal

This signal type is intended for rebalancing operations that should be performed on a known set of synths.

The *params* field should include a *synths* array and a *weights* array, of equal length. The *synths* array includes the relevant synths and the *weights* array includes the relative weights of each of the synths.

An example type2 signal indicating that the total balance of the sUSD, sETH, and sBTC assets should be rebalanced to 25% sUSD, 25% sETH, and 50% sBTC:

```
  {
    "execution_time": "2020-01-12T14:10:53Z",
    "params":
    {
      "synths": ["sUSD", "sETH", "sBTC" ],
      "weights": [1, 1, 2]
    }
    "name": "periodicRebalanceStrategy",
    "type": "type2"
  }
```

### type3 Trade Signal

This signal type is intended for swing trading between a pair of asset types. The signal directs the *signal server* to switch positions from the current synth of the pair to the other synth of the pair.

The *params* field should include a *pairs* array. The elements of the array should be one or more two-tuples indicating the pairs.

An example type3 signal indicating that the total balance of (sUSD, sETH) is to be switched from the synth that currently has the largest balance to the other synth:

```
  {
    "execution_time": "2020-01-12T14:10:53Z",
    "params":
    {
      "pairs": [ ["sUSD", "sETH"] ]
    }
    "name": "ETH20MACO",
    "type": "type3"
  }
```
