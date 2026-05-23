// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AegisAgent
 * @dev AegisAgent: Celo Ecosystem Intelligence - On-chain Subscription & Metrics Oracle
 * 
 * This contract enables:
 * 1. Subscription-based access to forensic analysis.
 * 2. On-chain logging of Forensic Health Scores (FHS) for verified Celo tokens.
 */
contract AegisAgent {
    address public owner;
    uint256 public subscriptionFee = 0.1 ether; // 0.1 CELO-S for a 24h pass
    uint256 public constant PASS_DURATION = 1 days;

    struct TokenMetric {
        string symbol;
        uint256 fhs;         // Forensic Health Score (multiplied by 10 for decimals, e.g. 7.5 -> 75)
        uint256 updatedAt;
        string phase;
    }

    // Mapping: User address => Expiry Timestamp
    mapping(address => uint256) public subscriptionExpiry;
    
    // Mapping: Token Address => Latest Metrics
    mapping(address => TokenMetric) public tokenMetrics;
    address[] public trackedTokens;

    event Subscribed(address indexed user, uint256 expiry);
    event MetricUpdated(address indexed token, string symbol, uint256 fhs, string phase);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }

    /**
     * @dev Buy a 24-hour access pass to AegisAgent Forensic Dashboard.
     */
    function subscribe() external payable {
        require(msg.value >= subscriptionFee, "Insufficient payment for subscription");
        
        uint256 currentExpiry = subscriptionExpiry[msg.sender];
        uint256 newExpiry = (currentExpiry > block.timestamp ? currentExpiry : block.timestamp) + PASS_DURATION;
        
        subscriptionExpiry[msg.sender] = newExpiry;
        emit Subscribed(msg.sender, newExpiry);
        
        // Refund surplus
        if (msg.value > subscriptionFee) {
            payable(msg.sender).transfer(msg.value - subscriptionFee);
        }
    }

    /**
     * @dev Check if a user has an active subscription.
     */
    function hasActiveSubscription(address _user) public view returns (bool) {
        return subscriptionExpiry[_user] > block.timestamp;
    }

    /**
     * @dev Update token metrics on-chain (Oracle function for the Aegis Agent).
     */
    function updateMetrics(address _token, string memory _symbol, uint256 _fhs, string memory _phase) external onlyOwner {
        if (tokenMetrics[_token].updatedAt == 0) {
            trackedTokens.push(_token);
        }
        
        tokenMetrics[_token] = TokenMetric({
            symbol: _symbol,
            fhs: _fhs,
            updatedAt: block.timestamp,
            phase: _phase
        });
        
        emit MetricUpdated(_token, _symbol, _fhs, _phase);
    }

    /**
     * @dev Withdraw collected fees to the owner.
     */
    function withdraw() external onlyOwner {
        payable(owner).transfer(address(this).balance);
    }

    /**
     * @dev Set a new subscription fee.
     */
    function setSubscriptionFee(uint256 _newFee) external onlyOwner {
        subscriptionFee = _newFee;
    }
}
