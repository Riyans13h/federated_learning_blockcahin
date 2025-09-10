// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract IncentiveSigned {
    struct RoundInfo {
        uint256 round;
        uint256 reward;
        uint256 shapley;
        uint256[] anomalies;
    }

    mapping(address => RoundInfo[]) public records;

    event RoundInfoSubmitted(
        address indexed client,
        uint256 round,
        uint256 reward,
        uint256 shapley,
        uint256[] anomalies
    );

    function submitSignedReward(
        uint256 round,
        uint256 reward,
        uint256 shapley,
        uint256[] memory anomalies,
        bytes memory signature
    ) public {
        // Encode the same data client signed off-chain (MUST match off-chain logic)
        bytes32 message = prefixed(
            keccak256(abi.encodePacked(round, reward, shapley, keccak256(abi.encodePacked(anomalies))))
        );
        address signer = recoverSigner(message, signature);
        require(signer != address(0), "Invalid signature");

        records[signer].push(RoundInfo(round, reward, shapley, anomalies));
        emit RoundInfoSubmitted(signer, round, reward, shapley, anomalies);
    }

    function getClientRecordCount(address client) public view returns (uint256) {
        return records[client].length;
    }

    function getLatestRecord(address client) public view returns (uint256, uint256, uint256, uint256[] memory) {
        RoundInfo memory r = records[client][records[client].length - 1];
        return (r.round, r.reward, r.shapley, r.anomalies);
    }

    // Signature recovery
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

    // Ethereum standard prefix
    function prefixed(bytes32 hash) internal pure returns (bytes32) {
        return keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", hash));
    }
}
