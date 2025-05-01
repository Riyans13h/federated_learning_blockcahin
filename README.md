
# 🤝 Federated Learning with Incentive Mechanism on Blockchain

This project implements a Federated Learning (FL) system where multiple clients collaboratively train a CNN model on MNIST data. Each client's contribution is measured using Monte Carlo Shapley values, and rewards are distributed through a smart contract deployed on the Ethereum blockchain.

---

## 📌 Features

- ✅ CNN-based Federated Learning (7 clients)
- ✅ Monte Carlo Shapley value computation
- ✅ Reinforcement Learning agent to adjust reward strategy
- ✅ Blockchain integration using Web3 and a deployed Ethereum smart contract
- ✅ Visualization of accuracy, contribution, and reward distribution
- ✅ Full automation and logging of each training round

---


```

---

## 🔧 Technologies Used

- Python, TensorFlow, NumPy, Matplotlib
- Web3.py for Ethereum smart contract interaction
- Solidity for writing the incentive contract
- MetaMask/Ganache/Testnet for blockchain testing
- Google Colab for running federated learning code

---

## 🧠 Federated Learning Setup

- **Dataset:** MNIST (Handwritten Digits)
- **Clients:** 7 clients, each trained locally on 1000 images
- **Model:** Convolutional Neural Network (CNN)
- **Rounds:** 6 training rounds
- **Aggregation:** Top-80% selection for first 3 rounds; full aggregation thereafter

---

## 💰 Incentive Mechanism

- **Shapley Value:** Monte Carlo approximation (3 permutations/round)
- **Reward Agent:** Reinforcement Learning Q-table adjusts per-client weights
- **Reward Distribution:** Done using `submitRoundInfo(round, reward, contribution)` to smart contract
- **Smart Contract:** Stores each round's rewards and contributions on the blockchain

---

## 🚀 How to Run

### 1. Clone the Project

```bash
git clone https://github.com/yourusername/federated-learning-blockchain.git
cd federated-learning-blockchain
```

### 2. Deploy Smart Contract (if needed)

Deploy `Incentive.sol` using Remix, Ganache, or Hardhat. Save the ABI as `Incentive.json` and update the contract address in the Python code.

### 3. Install Dependencies

```bash
pip install flwr tensorflow web3 matplotlib
```

### 4. Run Federated Learning

Open and run `federated_learning.py` in Google Colab or your local Jupyter environment.

---

## 📊 Output

- Final results table per round:
  - Accuracy
  - Normalized Shapley Value
  - Reward Value
  - Blockchain Transaction Hash

- Graphs:
  - Accuracy over rounds
  - Shapley values over rounds
  - Rewards over rounds

---

## 📈 Diagram

![Workflow](flowchart.png)

---

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for more information.

---

## 🤝 Acknowledgments

- [Flower Framework](https://flower.dev/)
- [Web3.py](https://web3py.readthedocs.io/)
- [Ethereum Remix IDE](https://remix.ethereum.org/)
- [Google Colab](https://colab.research.google.com/)
