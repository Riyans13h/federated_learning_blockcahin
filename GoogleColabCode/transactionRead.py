from web3 import Web3
import json

# ------------------------------
# CONFIGURATION
# ------------------------------
RPC_URL = "https://1e7d-2409-4089-ad81-adde-4a62-6652-2f5d-da8e.ngrok-free.app"
ABI_PATH = "/content/Incentive.json"  # Path to ABI file (exported from Remix or Truffle)
CONTRACT_ADDRESS = "0xE7069c455d3185F631ED3615B0386e5F963fAeaf"
TX_HASH = "0xd1d77fbb3030f4c9871cc14ad35c313db0f88a5b7bd7151946fc00b80062ea42"

# ------------------------------
# STEP 1: Connect to Ethereum Node
# ------------------------------
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    raise Exception("Failed to connect to Ethereum RPC")

print("Connected to Ethereum RPC")

# ------------------------------
# STEP 2: Load ABI
# ------------------------------
with open(ABI_PATH) as f:
    abi = json.load(f)['abi']

# ------------------------------
# STEP 3: Load Contract
# ------------------------------
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

# ------------------------------
# STEP 4: Fetch Transaction and Receipt by Hash
# ------------------------------
tx = w3.eth.get_transaction(TX_HASH)
receipt = w3.eth.get_transaction_receipt(TX_HASH)

# ------------------------------
# STEP 5: Print Basic Transaction Info
# ------------------------------
print("\nTransaction Info:")
print(f"Hash:         {TX_HASH}")
print(f"From:         {tx['from']}")
print(f"To:           {tx['to']}")
print(f"Value (ETH):  {w3.from_wei(tx['value'], 'ether')}")
print(f"Gas:          {tx['gas']}")
print(f"Nonce:        {tx['nonce']}")
print(f"Block Number: {tx['blockNumber']}")

# ------------------------------
# STEP 6: Print Receipt Info
# ------------------------------
print("\nTransaction Receipt:")
print(f"Status:        {'Success' if receipt['status'] == 1 else 'Failed'}")
print(f"Gas Used:      {receipt['gasUsed']}")
print(f"Contract Addr: {receipt['contractAddress']}")
print(f"Logs Count:    {len(receipt['logs'])}")

# ------------------------------
# STEP 7: Decode Logs (Event Data)
# ------------------------------
print("\nDecoded Event Logs:")
try:
    decoded_logs = contract.events.submitRoundInfo().process_receipt(receipt)
    if decoded_logs:
        for event in decoded_logs:
            print(f"Event: {event['event']}")
            for arg, val in event['args'].items():
                print(f"  {arg}: {val}")
    else:
        print("No events decoded.")
except Exception as e:
    print("Error decoding logs:", e)
