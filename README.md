# AI Mind Reader

A full-stack AI-powered game where an Artificial Intelligence tries to read your mind by asking up to 20 YES/NO questions. It uses a custom-trained Machine Learning model to evaluate features and make a highly accurate guess!

## Features
- **AI Guesses Mode:** You think of a secret object, and the AI asks smart questions to figure it out using a Decision Tree model.
- **You Guess Mode:** The AI picks a secret item, and you type natural language questions to guess what it is.
- **Dynamic Candidate Elimination:** Watch the AI narrow down its choices in real-time on the UI.
- **Full Model Transparency:** See exactly what features the AI is considering and how confident it is at any given step.

## Tech Stack
- **Frontend:** Svelte, Vite, standard CSS.
- **Backend:** Python, Flask, Scikit-learn, Pandas.
- **ML Model:** Decision Tree (ID3) classifier.

## How to Run Locally

### 1. Python Backend
Navigate to the backend folder:
```bash
cd backend
pip install -r requirements.txt  # If requirements exist, otherwise install pandas numpy scikit-learn flask flask-cors
python app.py
```
The Flask API will run on `http://localhost:5000`.

### 2. Svelte Frontend
Open a new terminal and navigate to the `frontend/` folder:
```bash
cd frontend
npm install
npm run dev
```
The web interface will typically run on `http://localhost:5173` (or whatever port Vite assigns, like 5174).

Enjoy the game!
