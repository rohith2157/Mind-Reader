<div align="center">
  <img src="https://assets.leetcode.com/users/images/307dc537-f823-4556-becd-fa9a27b8bfbc_1679047971.0543265.png" alt="AI Brain Logo" width="100"/>
  <h1>🧠 Mind Reader AI Game</h1>
  <p><strong>A Next-Generation Machine Learning Game that actually reads your mind.</strong></p>
  <p>
    <a href="#features">Features</a> •
    <a href="#tech-stack">Tech Stack</a> •
    <a href="#installation--running-locally">Installation</a> •
    <a href="#how-it-works">How It Works</a> •
    <a href="#models--accuracy">Machine Learning Models</a>
  </p>
</div>

---

## 🎮 The Experience

Mind Reader is a full-stack, AI-powered web game where you compete against a custom-trained **Decision Tree / Naive Bayes** ensemble. 

The game features two distinct modes:

1. **AI Guesses Mode:** You think of a secret object (like an animal, food, or vehicle). The AI will dynamically analyze the current candidate pool and heuristically choose the **best possible YES/NO questions** to ask you in order to narrow down its possibilities the fastest. Watch the AI's internal certainty scale up in real-time until it correctly guesses your thought!
2. **User Guesses Mode:** The tables turn! The AI secretly picks an object, and *you* must type natural language questions. The AI parses your semantics to answer you truthfully. Can you figure it out before you run out of questions?

---

## ✨ Features

- ⚡ **Dynamic Entropy Questions:** The AI dynamically recalculates information gain after every answer you provide to ask mathematically optimal questions.
- 🎯 **Visual Confidence Meter:** Watch the AI's certainty percentage increase as you answer, fully exposing the backend's Naive Bayes probabilities to the UI.
- 👀 **Live Candidate Elimination:** As you answer questions, you can actually look at the scrollable grid of potential identities. When you answer a question, you watch the incorrect items disappear instantly as the AI narrows you down.
- 🎨 **Glassmorphic UI:** Modern, highly stylized Svelte 4 frontend featuring gradients, glassmorphism, responsive candidate chips, and micro-animations.

---

## 🛠 Tech Stack

**Frontend:**
* [Svelte](https://svelte.dev/) (Component-based reactive UI)
* Vite (Rapid hot-reloading bundler)
* CSS 3 (Dynamic Keyframes, Gradients, Viewport sizing)

**Backend:**
* [Python 3](https://www.python.org/) & [Flask](https://flask.palletsprojects.com/) (REST APIs)
* [Scikit-Learn](https://scikit-learn.org/) (Model training and serialization)
* [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/) (Data structures & Math)

---

## 🚀 Installation & Running Locally

The project is structured neatly into decoupled `backend/` and `frontend/` workspaces so you can run the UI and the server independently.

### 1. Start the Machine Learning API (Backend)
Open a terminal in the repository root and navigate to the backend folder:
```bash
cd backend
pip install -r requirements.txt
python app.py
```
*The Flask server will start successfully on `http://127.0.0.1:5000` loading all pre-trained models from the `backend/models` directory into memory.*

### 2. Start the Game Engine UI (Frontend)
Open a **new** terminal in the repository root and navigate to the frontend folder:
```bash
cd frontend
npm install
npm run dev
```
*The Svelte client will start up instantly. `ctrl+click` the local network output (usually `http://localhost:5173` or `5174`) to play the game in your browser!*

---

## 📈 Models & Accuracy

The underlying datasets contain 189 unique items across diverse categories, scored against 40 binary features (e.g. `is_animal`, `has_wings`, `is_colorful`).

While the game is natively structured to utilize a **Decision Tree (ID3)** model due to its high interpretability when answering user queries, we have heavily optimized and analyzed multiple models!

| Model Type | Validation Accuracy | Cross-Validation Score (Mean) |
| :--- | :--- | :--- |
| **Logistic Regression** | **96.5%** | **93.3%** |
| Random Forest | 70.0% | 66.8% |
| Gradient Boosting | 68.0% | 65.5% |
| Naive Bayes | 61.5% | 71.0% |
| **Decision Tree (ID3)**| 60.5% | 55.3% |
| K-Nearest Neighbors | 83.5% | 78.8% |

*(Full technical documentation, evaluation graphs, confusion matrices, and model PKL files are located inside `backend/models/` and `backend/plots/`!)*
