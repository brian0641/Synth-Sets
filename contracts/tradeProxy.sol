/*

Contract to hold synths (Synthetix synths) on behalf of a user ("owner"). A designated third-party
("trader") may call the 'trade' function to place a synth trade on behalf of the owner. The trader
has no other control of the owner's funds. Only the owner can withdraw.

The constructor takes the following parameters:
owner:              The address of the owner.
trader:             The address of the trading service.
minMinsBtwTrades:   Successive trades will fail if not at least this many minutes apart. This parameter 
                      can be used to implement an extra layer of security to guard against the trader
                      overtrading the account.
feeRate:            Fee that is given to the trader for each trade. Can potentially be set to 0.
                    Units are basis points * 100. So 1% fee would be 10000. A 0.02% fee is 200.
*/

pragma solidity ^0.5.11;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/math/SafeMath.sol";

contract SynthetixInterface {
    function exchange(bytes32 sourceCurrencyKey, uint sourceAmount, bytes32 destinationCurrencyKey)
        external 
         returns (bool success);
         
    function synths(bytes32 currencyKey)
    public 
    view
    returns (address _address);
}

contract ERC20Interface {
    function transfer(address to, uint tokens) public returns (bool success);
    function balanceOf(address _owner) public view returns (uint256 balance);
}

contract tradeProxy {
    using SafeMath for uint;
    
    // ========== CONSTANTS ==========
    
    //mainnet
    address public synthetixContractAddress = 0xC011A72400E58ecD99Ee497CF89E3775d4bd732F;
    //kovan
    //address public synthetixContractAddress = 0x22f1ba6dB6ca0A065e1b7EAe6FC22b7E675310EF;
    
    // ========== STATE VARIABLES ==========
    address public owner;
    address public trader;
    bool public enableTrading = true;
    uint public minMinsBtwTrades;
    uint public feeRate;
    
    //User can optionally set a label for they trading strategy they would like implemented
    string public tradingStrategyLabel; 
    
    uint private lastTradeTS = 0;   //last trade timestamp
    mapping(bytes32 => uint) private feePoolBalances;  //store amounts owed to trader
    
    
    // The Synthetix contract address is a proxy address and should not change much (if it all). But
    // if it does, this contract would break. To guard against this, the Synthetix contract address may
    // be changed if both the Trader and the Owner agree (via calls to traderProposeNewAddress and 
    // ownerProposeNewAddress).
    address constant FAKE_ADDRESS = 0xB75Af109Ca1A6dB7c6B708E1292ee8fCc5b0B941;
    address public traderProposedNewAddress = FAKE_ADDRESS;
    address public ownerProposedNewAddress = FAKE_ADDRESS;


    // ========== CONSTRUCTOR ==========
    
    /**
     * @param  _owner The address of the Owner.
     * @param  _trader The address of the Trader.
     * @param  _minMinsBtwTrades Minimum time, in minutes, between trades. 
     * @param  _feeRate An optional fee that is given to the trader. Can be zero. The fee is taken from 
     *         the source synth for a trade. The units are basis points * 100. For example, a feeRate
     *         of 0.01% (one bp) would be passed as 100.
     */
    constructor(address _owner, 
                address _trader, 
                uint _minMinsBtwTrades,
                uint _feeRate) 
        public
    {
        owner = _owner;
        trader = _trader;
        minMinsBtwTrades = _minMinsBtwTrades;
        feeRate = _feeRate;
    }
    
    // ========== SETTER FUNCTIONS ==========
    function setEnableTrading(bool _enableTrading)
        public
    {
        require(msg.sender == owner, "Only the Owner can enable/disable trading");
        enableTrading = _enableTrading;
    }
    
    function setFeeRate(uint _feeRate)
        public
    {
        require(msg.sender == owner, "Only the Owner can set the fee rate.");
        feeRate = _feeRate; 
    }
    
    function setminMinsBtwTrades(uint _minMinsBtwTrades)
        public
    {
        require(msg.sender == owner, "Only the Owner can set the minutes between trades.");
        minMinsBtwTrades = _minMinsBtwTrades;
    }
    
    function setTraderAddress(address _trader)
        public
    {
        require(msg.sender == trader, "Only the Trader can change the Trader's address.");
        trader = _trader; 
    }
    
    
    function setTradeStratLabel(string memory _tradingStrategyLabel)
        public
    {
        require(msg.sender == owner, "Only the Owner can set the trade strategy label.");
        tradingStrategyLabel = _tradingStrategyLabel; 
        emit labelUpdate(_tradingStrategyLabel); 
    }
    
    
    // ========== FUNCTIONS ==========

    /**
     * @notice Withdraws synths from the contract to the owner.
     * @param  amount The amount (in wei) to withdraw.
     * @param  currencyKey The currency key of the synth to withdraw.  
     */
    function withdraw(uint amount, bytes32 currencyKey)
        external
        returns (bool)
    {
        require(msg.sender == owner);
        
        uint withdrawable = getBalance(currencyKey);
        
        //If they try to withdraw too much. Just give them their entire balance.
        uint _amount;
        if (amount > withdrawable)
        {
            _amount = withdrawable;
        } else {
            _amount = amount;
        }
        
        address synthAddress = SynthetixInterface(synthetixContractAddress).synths(currencyKey);
        return ERC20Interface(synthAddress).transfer(msg.sender, _amount);
    }
    
    
    /**
     * @notice Withdraws synths owed to the Trader. 
     * @param  amount The amount (in wei) to withdraw.
     * @param  currencyKey The currency key of the synth to withdraw.  
     */
    function withdrawTrader(uint amount, bytes32 currencyKey)
        public
        returns (bool)
    {
        require(msg.sender == trader);
        
        uint _amount;
        if (amount > feePoolBalances[currencyKey])
        {
            _amount = feePoolBalances[currencyKey];
        } else {
            _amount = amount;
        }
        
        address synthAddress = SynthetixInterface(synthetixContractAddress).synths(currencyKey);
        bool result = ERC20Interface(synthAddress).transfer(msg.sender, _amount);
        
        if (result) {
            feePoolBalances[currencyKey] = feePoolBalances[currencyKey].sub(_amount);
        }
        
        return result;
    }

    /**
     * @notice Trade synths via synthetix.exchange. Only callable by the Trader.
     *         The Owner can disable trading at any time by setting enableTrading to False.
     * @param  sourceCurrencyKey The currency key of the source synth.
     * @param  sourceAmount The amount (in wei) of the source synth.
     * @param  destinationCurrencyKey The currency key of the destination synth.
     * @param   minFeeRate If the feeRate set by the owner is less than this, the trade will revert.
     */
    function trade(bytes32 sourceCurrencyKey, 
                   uint sourceAmount,
                   bytes32 destinationCurrencyKey,
                   uint minFeeRate) 
        public
        returns (bool)
    {
        require(msg.sender == trader, "Only the Trader can call the trade function");
        require(enableTrading, "Trading is disabled");
        require(isTradeEligible(), "Not enough time has passed since last trade");
        require(feeRate >= minFeeRate, "Contract feeRate is too low.");
        
        uint feeAmount = feeForExchange(sourceAmount);
        uint _sourceAmount = sourceAmount.sub(feeAmount);   //reverts if result of subtraction is < zero
        
        bool result = SynthetixInterface(synthetixContractAddress).exchange(sourceCurrencyKey,
                   _sourceAmount, destinationCurrencyKey);
        
        if (result) {
            lastTradeTS = now;
            feePoolBalances[sourceCurrencyKey] += feeAmount; 
            //emit tradeEvent(sourceCurrencyKey, sourceAmount, destinationCurrencyKey);
        }
                   
        return result;
    }
    
    /**
     * @notice Allows the Trader to propose a new address for the Synthetix contract. Both the trader and 
     *         the owner must agree before the address is changed.
     * @param  newAddress The proposed new address for the Synthetix contract.
     */
    function traderProposeNewAddress(address newAddress)
        public
    {
        require(msg.sender == trader, "Only the Trader can call the traderProposedNewAddress function");
        
        traderProposedNewAddress = newAddress;
        
        if (traderProposedNewAddress == ownerProposedNewAddress && traderProposedNewAddress != FAKE_ADDRESS)
        {
            synthetixContractAddress = ownerProposedNewAddress;
        }
    }
    
    /**
     * @notice Allows the Owner to propose a new address for the Synthetix contract. Both the trader and 
     *         the owner must agree before the address is changed.
     * @param  newAddress The proposed new address for the Synthetix contract.
     */
    function ownerProposeNewAddress(address newAddress)
        public
    {
        require(msg.sender == owner, "Only the Owner can call the ownerProposedNewAddress function");
        
        ownerProposedNewAddress = newAddress;
        
        if (traderProposedNewAddress == ownerProposedNewAddress && traderProposedNewAddress != FAKE_ADDRESS)
        {
            synthetixContractAddress = ownerProposedNewAddress;
        }
    }
    
    // ========== VIEW FUNCTIONS ==========

    
    /**
     * @return boolean whether the minimum time between trades has elapsed.
     * */
    function isTradeEligible()
        public
        view
        returns (bool)
    {
        if (now - lastTradeTS > (minMinsBtwTrades * 60) )
        {
            return true;
        }
        return false;
    }
    
    /**
     * @return The Owner's balance, in wei, for the synth. 
     * */
    function getBalance(bytes32 currencyKey)
        public
        view
        returns (uint)
    {
        address synthAddress = SynthetixInterface(synthetixContractAddress).synths(currencyKey);
        uint totalBal = ERC20Interface(synthAddress).balanceOf(address(this));
        
        if (totalBal <= feePoolBalances[currencyKey]) 
        {
            return 0;
        }
        return totalBal - feePoolBalances[currencyKey];
    }
    
    /**
     * @return The Traders's balance, in wei, for the synth. 
     * @param currencyKey  The currency key of the synth for which the balance is to be fetched.
     * */
    function getBalanceTrader(bytes32 currencyKey)
        public
        view
        returns (uint)
    {
        return feePoolBalances[currencyKey];
    }
    
    /**
     * @notice Calculates the fee amount, based on the feeRate, that is given to Trader.
     * @param  amount  The amount (the source amount) for the trade.
     */
    function feeForExchange(uint amount)
        public
        view
        returns (uint)
    {
        uint _feeAmount = amount.mul(feeRate);
        _feeAmount = _feeAmount.div(1000000);
        
        return _feeAmount;
    }
    
    // ========== EVENTS ==========
    event tradeEvent(bytes32 _sourceCurrencyKey, 
                   uint _sourceAmount,
                   bytes32 _destinationCurrencyKey);
                   
    event labelUpdate(string newLabel); 
      

}
