pragma solidity ^0.5.11;

contract SynthetixInterface {
    function exchange(bytes32 sourceCurrencyKey, uint sourceAmount, bytes32 destinationCurrencyKey)
        external 
         returns (bool success);
}

contract ERC20Interface {
    function transfer(address to, uint tokens) public returns (bool success);
    function balanceOf(address _owner) public view returns (uint256 balance);
}
