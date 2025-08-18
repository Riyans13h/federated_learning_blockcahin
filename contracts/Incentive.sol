// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract IncentiveSigned {
    struct RoundInfo {
        uint256 round;
        uint256 reward;
        uint256 shapley;
    }

    mapping(address => RoundInfo[]) public records;

    event RoundInfoSubmitted(address indexed client, uint256 round, uint256 reward, uint256 shapley);

    function submitSignedReward(
        uint256 round,
        uint256 reward,
        uint256 shapley,
        bytes memory signature
    ) public {
        bytes32 message = prefixed(keccak256(abi.encodePacked(round, reward, shapley)));
        address signer = recoverSigner(message, signature);
        require(signer != address(0), "Signature invalid");

        records[signer].push(RoundInfo(round, reward, shapley));
        emit RoundInfoSubmitted(signer, round, reward, shapley);
    }

    function getClientRecordCount(address client) public view returns (uint) {
        return records[client].length;
    }

    function getLatestRecord(address client) public view returns (uint, uint, uint) {
        RoundInfo memory r = records[client][records[client].length - 1];
        return (r.round, r.reward, r.shapley);
    }

    function recoverSigner(bytes32 message, bytes memory sig) internal pure returns (address) {
        require(sig.length == 65, "Invalid signature length");

        bytes32 r;
        bytes32 s;
        uint8 v;

        assembly {
            r := mload(add(sig, 32))
            s := mload(add(sig, 64))
            v := byte(0, mload(add(sig, 96)))
        }

        return ecrecover(message, v, r, s);
    }

    function prefixed(bytes32 hash) internal pure returns (bytes32) {
        return keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", hash));
    }
}
