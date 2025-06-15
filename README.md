# Race-Strategy-AI-F1-NFS
AI agent for NFS Most Wanted using Deep RL (Soft Actor-Critic). Learns fastest lap times by self-driving at full speed, reading game memory via custom API, correcting mistakes, and improving performance using expert data, OpenAI Gym, PyTorch, and real-time game control.
This project implements an autonomous racing agent that learns optimal lap times in *Need for Speed: Most Wanted* using **Deep Reinforcement Learning (DRL)** inspired by Formula 1 race strategies.
The agent races automatically at full speed, learns from collisions and off-track mistakes, and iteratively improves lap times using advanced self-learning algorithms.

---

## 🚀 Key Features

- 🧠 **Reinforcement Learning** with Soft Actor-Critic (SAC)
- 🎮 **Game memory hacking** using Cheat Engine & custom API
- 🔄 **Real-time control** via virtual gamepad interface
- 📊 **Custom OpenAI Gym environment** for training
- 🏁 Learns from both **self-play & expert gameplay data**
- 📈 Progressive lap-time optimization

---

## 🛠 Tech Stack

- Python
- PyTorch
- OpenAI Gym
- Stable-Baselines3
- Soft Actor-Critic (SAC)
- Cheat Engine / Memory Hacking Tools
- Virtual Game Controller APIs

---

## 🖥️ Setup Instructions

1️⃣ Clone the repository:

```bash
git clone https://github.com/yourusername/F1-NFS-RaceStrategy-AI.git
cd F1-NFS-RaceStrategy-AI

2️⃣ Create virtual environment:

python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

3️⃣ Install dependencies:

pip install -r requirements.txt

4️⃣ Install and configure Cheat Engine or MemExplorer to extract game memory addresses.

5️⃣ Run training:

python train.py

📊 Results
AI agent successfully achieves continuous lap time improvement

Demonstrates learning from self-driving errors, crashes, and off-track behavior

Competitively matches human lap times after sufficient training

🔐 Disclaimer
Game memory modification done purely for research purposes.

No commercial or multiplayer usage involved.

Please respect applicable terms of use when replicating.

📩 Contact
For collaboration or questions:
[Aravindan TM] —  [www.linkedin.com/in/aravindantm]

