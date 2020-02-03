# Synth-Sets

[Synthetix](https://www.synthetix.io/) is a crypto-backed synthetic asset platform. There are number of synthetic assets (synths), including a synthetic gold (sXAU), synthetic bitcoin (sBTC), and synthetix Ethereum (sETH). The various synth assets can be exchanged for one another using prices published by a price Oracle and with no slippage other than an exchange fee.

[TokenSets](https://www.tokensets.com/) is a project that issues single ERC20 tokens that each represent an automatically rebalancing portfolio. Different portfolios rebalance based on different trading strategies. Users occur rebalancing slippage whenever a portfolio rebalances. Rebalancing slippage can be 0.6% and higher.   

This project uses the TokenSet signals to mimic the TokenSet performance using synths. The infinite liquidity and lower transaction fees of the Synthetix system should produce superior long-term performance relative to TokenSets.

## Implementation

There are two main functional components in Synth-Sets:

+ An Ethereum **smart contract** that holds synths for a user ("Owner"). Only the Owner can transfer the synths outside of the smart contract. When creating the smart contract, the Owner can designate a second address as a *Trader* address. The Trader can initiate trades in the synth ecosystem, but otherwise has no control over the Owner's funds. Only the Owner can withdraw.

+ A server process, called the **trade signal server**, acts as the Trader and generates the trade signals for the smart contract. The server pulls the trade signals from the TokenSets project. The server is a light process and can be run by anyone. Or you can skip this step and instead hook into someone else's server.    

From a security perspective, running your own server is more secure than using a third-party server. However, using a third-party server is not as insecure as may be initially imagined. Trades are limited to trades within the Synthetix ecosystem. There are no inherently bad trades. Or stated differently, it is no easier to predict "bad" trades than it is to predict "good" trades.

Additionally, the smart contract allows the Owner to specify a minimum time between trades. So if the intent is to follow a TokenSet that rebalances no more than once a week, this parameter would be set to allow no more than one trade a week. At anytime the Owner can disable trading or withdraw their funds.  

## Architecture (blockchain)

The Ethereum smart contract architecture is very simple. The main contract is "tradeProxy.sol," an instance of which is deployed for each user. tradeProxy allows the person that deploys the contract (the Owner) to designate another address (the Trader) to place synth trades on behalf of the Owner. The Trader has no other control of the owner's funds. Only the Owner can withdraw synths.   

A factory contract (tradeProxyFactory.sol) is used to create and track new instances of tradeProxy. The current address of the factory contract is:
* **Mainnet**: COMING-SOON
* **Kovan testnet** : 0x1F211b8Ea061F6b90153e9d4B2FBE3808b574aA8

The main functions/parameters that are implemented by tradeProxy, and which are settable only by the Owner, include:
* *Enable/Disable Trading.* The Owner can, at any time, enable or disable synth trading by the Trader.

* *Minimum Minutes Between Trades.* This is the minimum minutes required between trades. Can be used as a safeguard against over trading by the Trader. E.g., for a strategy that trades no more than once a day, this should be set to 1440 (60*24).

* *Allowable Synths To Trade.* List of synths that the owner designates as synths that are eligible for trading. For example, a swing trading strategy that alternates between sETH and sUSD may set this parameter to limit trading to these two synths.

* *Trade Strategy (string).* The is a label that the Owner uses to indicate which automated strategy they wish to have implemented on their synths.

* *Withdraw*.  Used to withdraw synths from the contract to the Owner's address.

## Architecture (server-side)

A server process is needed to act as the Trader to generate the trade signals for the contracts. A design goal of this project is to make it as easy as possible for users to either run their own server or hook into another server. The server processes are divided into two separate processes:
* A *signal server* that receives the trade signals and handles submitting the corresponding Ethereum transactions to the blockchain.

* *Signal generators* that source the trade signals. Currently, a TokenSets generator is implemented (/signal_generators/TokenSets_Generator/) to pull TokenSet signals from the TokenSet smart contracts and a manual generator is implemented (/signal_generators/Manual_Generator/) to allow trades to manually be input via a text file (this one is mostly for testing).


## UI

There is currently no easy graphical interface. This is a high priority and will be implemented next.
