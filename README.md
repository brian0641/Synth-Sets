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

The following diagram summarizes the components of Synth-Sets:

*A cool diagram goes here*

## Tutorials

There is currently no easy graphical interface to deploy the smart contract or trade signal server (coming eventually I hope). The following tutorials describe "manual" deployment of the smart contract, connecting to an existing trade signal server, and installation of a new trade signal server.

+ smart contract deployment  
+ connection to tss  
+ installation of new tss  
