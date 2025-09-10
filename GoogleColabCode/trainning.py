# ============================ [ COLAB SERVER CELL ] ============================
!pip install flask-ngrok flask tensorflow

from flask_ngrok import run_with_ngrok
from flask import Flask, request, jsonify
import numpy as np
import tensorflow as tf
import random

app = Flask(__name__)
run_with_ngrok(app)

clients_data = {}
results = []
round_number = 0
global_model = None

(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
x_test = x_test[..., None] / 255.0
y_test = y_test

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

def average_weights(models):
    return [np.mean([w[i] for w in models], axis=0) for i in range(len(models[0]))]

def evaluate_model(model, x, y):
    return model.evaluate(x, y, verbose=0)[1]

def monte_carlo_shapley(models, rounds=5):
    n, shapley = len(models), [0.0]*len(models)
    for _ in range(rounds):
        perm, acc, temp = random.sample(range(n), n), 0, []
        for idx in perm:
            temp.append(models[idx])
            m = build_model()
            m.set_weights(average_weights(temp))
            new_acc = evaluate_model(m, x_test, y_test)
            shapley[idx] += new_acc - acc
            acc = new_acc
    return [s/rounds for s in shapley]

class RLRewardAgent:
    def __init__(self, n, base_reward=1000):
        self.q_table = [1.0]*n
        self.base = base_reward
        self.lr = 0.1

    def update(self, idx, reward, acc):
        self.q_table[idx] += self.lr * (acc - self.q_table[idx])

    def get_rewards(self, norm_shap):
        return [max(0, int(s * self.base * self.q_table[i])) for i, s in enumerate(norm_shap)]

agent = RLRewardAgent(n=7)

@app.route("/")
def home():
    return "✅ Federated Server is Running with REST API!"

@app.route("/upload_model", methods=["POST"])
def upload_model():
    data = request.get_json()
    cid = int(data["client_id"])
    weights = [np.array(w) for w in data["weights"]]
    clients_data[cid] = weights
    print(f"📥 Client {cid} model received ({len(clients_data)}/7)")
    return jsonify({"status": "Model received", "client_id": cid})

@app.route("/aggregate", methods=["POST"])
def aggregate():
    global clients_data, global_model, round_number, results

    if len(clients_data) < 7:
        return jsonify({"error": "Need 7 clients to aggregate"}), 400

    local_models = [clients_data[i] for i in sorted(clients_data)]
    client_ids = sorted(clients_data)
    shap = monte_carlo_shapley(local_models, rounds=5)
    mean_shap, std_shap = np.mean(shap), np.std(shap)
    anomalies = [client_ids[i] for i, s in enumerate(shap) if s < mean_shap - 2*std_shap]

    filtered_models = [local_models[i] for i in range(7) if client_ids[i] not in anomalies]
    filtered_shap = [shap[i] for i in range(7) if client_ids[i] not in anomalies]

    selected = filtered_models
    if round_number <= 2:
        top_k = int(0.8 * len(filtered_models))
        top_idx = sorted(range(len(filtered_shap)), key=lambda i: filtered_shap[i], reverse=True)[:top_k]
        selected = [filtered_models[i] for i in top_idx]

    avg_weights = average_weights(selected)
    if global_model is None:
        global_model = build_model()
    global_model.set_weights(avg_weights)

    total = sum(filtered_shap)
    norm_shap = [s / total if total > 0 else 0 for s in filtered_shap]
    rewards = agent.get_rewards(norm_shap)
    for i in range(len(rewards)):
        agent.update(i, rewards[i], filtered_shap[i])

    round_number += 1
    results.append({
        "round": round_number,
        "shap": shap,
        "rewards": rewards,
        "anomalies": anomalies
    })

    clients_data = {}
    return jsonify({
        "status": "aggregated",
        "round": round_number,
        "shapley": shap,
        "anomalies": anomalies,
        "rewards": rewards
    })

@app.route("/results", methods=["GET"])
def get_results():
    return jsonify(results)

app.run()








###########################################################################################################################################################################


import requests
import tensorflow as tf
import numpy as np

# Replace with your actual ngrok URL from the server output
server_url = "http://<your-ngrok-url>.ngrok.io"

client_id = int(input("Enter Client ID (0-6): "))
is_poisoned = client_id == 6

(x_train, y_train), _ = tf.keras.datasets.mnist.load_data()
x_train = x_train[..., None] / 255.0

x_local = x_train[client_id*1000:(client_id+1)*1000]
y_local = y_train[client_id*1000:(client_id+1)*1000]

if is_poisoned:
    print(f"[⚠️] Client {client_id} is poisoned (label flipping)")
    y_local = (y_local + 5) % 10

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

model = build_model()
model.fit(x_local, y_local, epochs=3, batch_size=64, verbose=0)
weights = model.get_weights()

payload = {
    "client_id": str(client_id),
    "weights": [w.tolist() for w in weights]
}

res = requests.post(f"{server_url}/upload_model", json=payload)
print(res.json())

# Only client 0 triggers aggregation
if client_id == 0:
    agg = requests.post(f"{server_url}/aggregate")
    print("🔁 Aggregation Result:", agg.json())

res = requests.get(f"{server_url}/results")
print("📊 All Rounds Summary:")
print(res.json())
