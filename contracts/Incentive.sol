
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Incentive {
    struct RoundInfo {
        uint256 round;
        uint256 reward;
        uint256 shapley;
    }

    mapping(address => RoundInfo[]) public records;

    // Define the event for logging
    event RoundInfoSubmitted(address indexed client, uint256 round, uint256 reward, uint256 shapley);

    function submitRoundInfo(uint256 round, uint256 reward, uint256 shapley) public {
        records[msg.sender].push(RoundInfo(round, reward, shapley));
        
        // Emit the event to log the submission
        emit RoundInfoSubmitted(msg.sender, round, reward, shapley);
    }

    function getClientRecordCount(address client) public view returns (uint) {
        return records[client].length;
    }

    function getLatestRecord(address client) public view returns (uint, uint, uint) {
        RoundInfo memory r = records[client][records[client].length - 1];
        return (r.round, r.reward, r.shapley);
    }
}
   