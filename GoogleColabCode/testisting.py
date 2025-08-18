from web3 import Web3
import json

# STEP 1: Connect to your Ethereum node (replace with your ngrok RPC)
w3 = Web3(Web3.HTTPProvider("https://1e7d-2409-4089-ad81-adde-4a62-6652-2f5d-da8e.ngrok-free.app"))

# STEP 2: Load contract ABI
with open("/content/Incentive.json") as f:
    abi = json.load(f)["abi"]

# STEP 3: Setup contract
contract_address = "0xE7069c455d3185F631ED3615B0386e5F963fAeaf"
contract = w3.eth.contract(address=contract_address, abi=abi)

# STEP 4: Provide the transaction hash
tx_hash = "0xd1d77fbb3030f4c9871cc14ad35c313db0f88a5b7bd7151946fc00b80062ea42"

# STEP 5: Get Transaction Info
tx = w3.eth.get_transaction(tx_hash)
receipt = w3.eth.get_transaction_receipt(tx_hash)

# Print Transaction Info
print("🔹 Transaction Info")
print(f"Hash: {tx_hash}")
print(f"From: {tx['from']}")
print(f"To: {tx['to']}")
print(f"Value: {w3.from_wei(tx['value'], 'ether')} ETH")
print(f"Gas: {tx['gas']}")
print(f"Nonce: {tx['nonce']}")
print(f"Block Number: {tx['blockNumber']}")

# Print Receipt Info
print("\n🔹 Receipt Info")
print(f"Block Number: {receipt['blockNumber']}")
print(f"Gas Used: {receipt['gasUsed']}")
print(f"Status: {'Success ' if receipt['status'] == 1 else 'Failed '}")
print(f"Contract Address: {receipt['contractAddress']}")
print(f"Logs: {len(receipt['logs'])}")

# STEP 6: Decode Logs (if any)
print("\n🔹 Decoded Logs:")
try:
    decoded_logs = contract.events.submitRoundInfo().process_receipt(receipt)
    if decoded_logs:
        for event in decoded_logs:
            print(f" Event: {event['event']}")
            for arg, val in event['args'].items():
                print(f"   - {arg}: {val}")
    else:
        print(" No matching event logs found.")
except Exception as e:
    print(" Log decoding failed:", e)
