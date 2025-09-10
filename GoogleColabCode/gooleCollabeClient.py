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
