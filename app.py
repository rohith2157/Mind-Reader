"""
app.py — Flask Web Application for AI Mind Reader
# Exp-12: Full project integration — Web interface
"""

from flask import Flask, render_template, request, jsonify, session, send_from_directory
from flask_cors import CORS
import os
import json

from game_engine import MindReaderGame

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Global game instance
game = MindReaderGame()


# ═══════════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/')
def home():
    """Home screen with game mode selection."""
    score = game.get_score()
    return render_template('index.html', score=score)


@app.route('/game/<mode>')
def game_page(mode):
    """Game screen — mode is 'ai_guesses' or 'user_guesses'."""
    if mode not in ('ai_guesses', 'user_guesses'):
        return "Invalid mode", 400
    return render_template('game.html', mode=mode)


@app.route('/stats')
def stats_page():
    """Stats dashboard."""
    stats = game.get_stats()
    # Load model accuracies
    accuracies = {}
    if os.path.exists('model_accuracy.json'):
        with open('model_accuracy.json', 'r') as f:
            accuracies = json.load(f)
    return render_template('stats.html', stats=stats, accuracies=accuracies)


# ═══════════════════════════════════════════════════════════════════════════
# AI GUESSES MODE API
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/ai-guess/start', methods=['POST'])
def ai_guess_start():
    """Start a new AI guesses game."""
    game.start_ai_guesses_mode()
    question = game.get_next_question()
    return jsonify({
        'status': 'started',
        'question': question,
        'candidates': game.get_candidates_list(),
    })


@app.route('/api/ai-guess/answer', methods=['POST'])
def ai_guess_answer():
    """Process user's YES/NO answer."""
    data = request.get_json()
    feature = data.get('feature')
    answer = data.get('answer')  # True/False

    result = game.answer_question(feature, answer)

    if result['should_guess']:
        guess = game.make_guess()
        return jsonify({
            'status': 'guessing',
            'guess': guess,
            'result': result,
            'candidates': game.get_candidates_list(),
        })

    next_question = game.get_next_question()
    return jsonify({
        'status': 'continue',
        'question': next_question,
        'result': result,
        'candidates': game.get_candidates_list(),
    })


@app.route('/api/ai-guess/finalize', methods=['POST'])
def ai_guess_finalize():
    """Record whether AI's guess was correct."""
    data = request.get_json()
    correct = data.get('correct', False)
    score = game.finalize_ai_guess(correct)
    return jsonify({'score': score})


# ═══════════════════════════════════════════════════════════════════════════
# USER GUESSES MODE API
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/user-guess/start', methods=['POST'])
def user_guess_start():
    """Start a new user guesses game."""
    result = game.start_user_guesses_mode()
    return jsonify({
        'status': 'started',
        'message': result['message'],
    })


@app.route('/api/user-guess/ask', methods=['POST'])
def user_guess_ask():
    """User asks a question about the secret object."""
    data = request.get_json()
    question = data.get('question', '')
    result = game.answer_user_question(question)
    return jsonify(result)


@app.route('/api/user-guess/hint', methods=['POST'])
def user_guess_hint():
    """User requests a hint."""
    result = game.get_hint()
    return jsonify(result)


@app.route('/api/user-guess/guess', methods=['POST'])
def user_guess_check():
    """User makes a guess."""
    data = request.get_json()
    guess = data.get('guess', '')
    result = game.check_user_guess(guess)
    result['score'] = game.get_score()
    return jsonify(result)


@app.route('/api/user-guess/give-up', methods=['POST'])
def user_guess_give_up():
    """User gives up."""
    result = game.give_up()
    result['score'] = game.get_score()
    return jsonify(result)


# ═══════════════════════════════════════════════════════════════════════════
# STATS API
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/stats')
def api_stats():
    """Return game stats."""
    stats = game.get_stats()
    accuracies = {}
    if os.path.exists('model_accuracy.json'):
        with open('model_accuracy.json', 'r') as f:
            accuracies = json.load(f)
    return jsonify({'stats': stats, 'accuracies': accuracies})


@app.route('/api/score')
def api_score():
    """Return current score."""
    return jsonify(game.get_score())


# ═══════════════════════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("\n🧬 AI Mind Reader — Starting Web Server...")
    print("   Open http://127.0.0.1:5000 in your browser\n")
    app.run(debug=True, host='127.0.0.1', port=5000)
