# STEP 1: Install libraries (run once in Colab)
# !pip install flwr tensorflow web3 matplotlib

# STEP 2: Imports
import tensorflow as tf
import numpy as np
from web3 import Web3
import json, random
import matplotlib.pyplot as plt

# STEP 3: Model Definition (CNN-style to improve accuracy)
def build_model():
    model = tf.keras.Sequential([
        tf.keras.layers.InputLayer(input_shape=(28, 28, 1)),
        tf.keras.layers.Conv2D(32, (3,3), activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(10, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

# STEP 4: Load & Prepare Data (use 7 clients, enough data per client)
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
x_train, x_test = x_train[..., None]/255.0, x_test[..., None]/255.0
clients = [(x_train[i*1000:(i+1)*1000], y_train[i*1000:(i+1)*1000]) for i in range(7)]  # ⬅️ 7 clients

# STEP 5: Averaging + Evaluation + Monte Carlo Shapley
def average_weights(models):
    base = build_model()
    weights = [m.get_weights() for m in models]
    avg = [np.mean([w[i] for w in weights], axis=0) for i in range(len(weights[0]))]
    base.set_weights(avg)
    return base

def evaluate_model(model):
    return model.evaluate(x_test, y_test, verbose=0)[1]

def monte_carlo_shapley(models, rounds=10):
    n, shapley = len(models), [0.0]*len(models)
    for _ in range(rounds):
        perm, acc, temp = random.sample(range(n), n), 0, []
        for idx in perm:
            temp.append(models[idx])
            model = average_weights(temp)
            new_acc = evaluate_model(model)
            shapley[idx] += new_acc - acc
            acc = new_acc
    return [s/rounds for s in shapley]

# STEP 6: RL Agent
class RLRewardAgent:
    def __init__(self, n, base_reward=1000):
        self.q_table = [1.0]*n
        self.base = base_reward
        self.lr = 0.1

    def update(self, idx, reward, acc):
        self.q_table[idx] += self.lr * (acc - self.q_table[idx])

    def get_rewards(self, norm_shap):
        return [max(0, int(s * self.base * self.q_table[i])) for i, s in enumerate(norm_shap)]

# STEP 7: Blockchain Setup (Update your values)
w3 = Web3(Web3.HTTPProvider("https://41d4-2409-4089-ad81-adde-57d1-2311-e844-3daf.ngrok-free.app"))
with open("/content/Incentive.json") as f:
    abi = json.load(f)['abi']
contract = w3.eth.contract(address='0xB418D99ecF07bb3DfA6a2C8DBAB213c5Aa7FC95D', abi=abi)
sender = w3.eth.accounts[0]

# STEP 8: Federated Rounds
global_model = build_model()
agent = RLRewardAgent(n=7)  # ⬅️ 7 clients
results = []

for r in range(6):  # ⬅️ 6 rounds
    print(f"\n Round {r+1}")
    local_models, accs = [], []

    for i in range(7):  # ⬅️ 7 clients
        model = build_model()
        model.set_weights(global_model.get_weights())
        model.fit(clients[i][0], clients[i][1], epochs=3, batch_size=64, verbose=0)
        acc = evaluate_model(model)
        local_models.append(model)
        accs.append(acc)

    if r <= 2:  # First 3 rounds: top 80%
        top_count = int(0.8 * len(accs))  #  top 80% of 7 = 5
        top_idx = sorted(range(len(accs)), key=lambda i: accs[i], reverse=True)[:top_count]
        global_model = average_weights([local_models[i] for i in top_idx])
    else:
        global_model = average_weights(local_models)

    shap = monte_carlo_shapley(local_models, rounds=3)
    total = sum(shap)
    norm_shap = [s / total if total > 0 else 0 for s in shap]
    rewards = agent.get_rewards(norm_shap)

    tx_hashes = []
    for i in range(7):  #  7 clients
        reward = max(0, rewards[i])  # Ensure reward is non-negative
        scaled_shap = max(0, int(norm_shap[i]*100))  # Ensure uint-compatible
        tx = contract.functions.submitRoundInfo(r+1, reward, scaled_shap).transact({'from': sender})
        receipt = w3.eth.wait_for_transaction_receipt(tx)
        tx_hashes.append(receipt.transactionHash.hex())
        agent.update(i, reward, accs[i])

    results.append({
        "round": r+1,
        "acc": accs,
        "shap": norm_shap,
        "reward": rewards,
        "hash": tx_hashes
    })

# STEP 9: Output Table
print("\n📊 Final Results Table")
for r in results:
    print(f"\n Round {r['round']}")
    print(f"{'Client':<8}{'Accuracy':<10}{'Shapley':<10}{'Reward':<10}{'TxHash'}")
    for i in range(7):  # ⬅️ 7 clients
        print(f"{i:<8}{r['acc'][i]:.4f}   {r['shap'][i]:.4f}   {r['reward'][i]:<10}{r['hash'][i][:75]}")

# STEP 10: Plot Results
rounds = [r['round'] for r in results]
for label in ['acc', 'shap', 'reward']:
    plt.figure(figsize=(8, 4))
    for i in range(7):  # ⬅️ 7 clients
        plt.plot(rounds, [r[label][i] for r in results], label=f'Client {i}')
    plt.title(f"{label.capitalize()} over Rounds")
    plt.xlabel("Round")
    plt.ylabel(label.capitalize())
    plt.legend()
    plt.grid(True)
    plt.show()
