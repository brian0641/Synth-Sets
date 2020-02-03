pragma solidity ^0.5.11;

import {tradeProxy} from "tradeProxy.sol";

contract tradeProxyFactory {
  // index of created contracts
  address[] public tradeProxyContracts;

  function getContractCount() 
    public
    view
    returns(uint contractCount)
  {
    return tradeProxyContracts.length;
  }

  /**
     * @notice Deploy a new tradeProxy contract through the factory.
     * @param  _owner The address of the Owner.
     * @param  _trader The address of the Trader.
     * @param  _minMinsBtwTrades Minimum time, in minutes, between trades. 
     * @param  _feeRate An optional fee that is given to the trader. Can be zero. The fee is taken from 
     *         the source synth for a trade. The units are basis points * 100. For example, a feeRate
     *         of 0.01% (one bp) would be passed as 100.
     * @param  _tradingStrategyLabel Label to indicate which strategy is to be implemented for this
     *         contract.
     */
  function newTradeProxyContract(
                address _owner, 
                address _trader, 
                uint _minMinsBtwTrades,
                uint _feeRate,
                string memory _tradingStrategyLabel)  
    public
    returns(address newContract)
  {
    address tp = address(new tradeProxy(_owner, _trader, _minMinsBtwTrades, 
                                   _feeRate, _tradingStrategyLabel));
    tradeProxyContracts.push(tp);
    
    //emit indication of new contract created
    emit tradeProxyCreated(tp);
    
    return tp;
  }
  
  
  // ========== EVENTS ==========
    event tradeProxyCreated(address _newContractAddress);
}
