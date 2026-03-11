"""
game_engine.py — Core Game Logic for AI Mind Reader
Uses Decision Tree (ID3) model trained via Google Colab notebook.
Model loaded from models/modelcolab/
"""

import pandas as pd
import numpy as np
import json
import os
import random
import joblib
from datetime import datetime


class MindReaderGame:
    """
    AI Mind Reader Game Engine.
    
    MODE 1 — AI GUESSES: User thinks, AI asks YES/NO questions.
    MODE 2 — USER GUESSES: AI picks object, user asks YES/NO questions.
    """

    # Human-readable question map for each feature
    QUESTION_MAP = {
        'is_alive': "Is it alive (or was it once alive)?",
        'is_animal': "Is it an animal?",
        'is_human': "Is it a human or human-like?",
        'is_plant': "Is it a plant?",
        'is_object': "Is it a non-living object?",
        'has_wings': "Does it have wings?",
        'can_fly': "Can it fly?",
        'lives_in_water': "Does it live in or near water?",
        'lives_in_jungle': "Does it live in a jungle or forest?",
        'lives_in_desert': "Does it live in a desert?",
        'lives_in_home': "Can it be found in a home?",
        'is_big': "Is it bigger than a dog?",
        'is_small': "Is it smaller than a cat?",
        'has_4_legs': "Does it have 4 legs?",
        'has_2_legs': "Does it walk on 2 legs?",
        'has_no_legs': "Does it have no legs?",
        'has_fur': "Does it have fur or hair?",
        'has_scales': "Does it have scales?",
        'has_feathers': "Does it have feathers?",
        'has_shell': "Does it have a shell or hard covering?",
        'is_carnivore': "Is it a meat-eater (carnivore)?",
        'is_herbivore': "Is it a plant-eater (herbivore)?",
        'is_omnivore': "Does it eat both plants and meat?",
        'is_dangerous': "Is it dangerous to humans?",
        'is_domestic': "Is it domesticated or commonly kept by humans?",
        'is_nocturnal': "Is it mainly active at night (nocturnal)?",
        'found_in_africa': "Can it be found in Africa?",
        'found_in_asia': "Can it be found in Asia?",
        'found_in_ocean': "Can it be found in the ocean?",
        'is_fast': "Is it fast-moving?",
        'is_colorful': "Is it colorful?",
        'makes_sound': "Does it make notable sounds?",
        'can_be_pet': "Can it be kept as a pet?",
        'is_extinct': "Is it extinct?",
        'is_fictional': "Is it fictional or mythological?",
        'is_used_daily': "Is it used in daily life?",
        'is_electronic': "Is it electronic or uses electricity?",
        'is_food_related': "Is it related to food or cooking?",
        'is_vehicle': "Is it a vehicle or used for transport?",
        'is_used_in_sports': "Is it used in sports?",
    }

    def __init__(self):
        """Load all trained models and dataset."""
        self.models = {}
        self.df = None
        self.feature_cols = None
        self.le_name = None
        self.le_category = None
        self.score = {'ai_wins': 0, 'user_wins': 0}
        self.game_history = []
        self.current_game = None

        self._load_resources()
        self._load_history()

    def _load_resources(self):
        """Load model, encoders, and dataset."""
        # Load dataset
        self.df = pd.read_csv('mindreader_data.csv')

        # Load from modelcolab (trained via Colab notebook)
        model_dir = 'models/modelcolab'

        # Load feature columns
        self.feature_cols = joblib.load(f'{model_dir}/feature_cols.pkl')

        # Load label encoders
        self.le_name = joblib.load(f'{model_dir}/label_encoder_name.pkl')
        self.le_category = joblib.load(f'{model_dir}/label_encoder_category.pkl')

        # Decision Tree — Only model (trained in Colab notebook)
        self.models['dt'] = joblib.load(f'{model_dir}/dt_model.pkl')

        # Get unique entities for candidate filtering
        self.unique_entities = self.df.drop_duplicates(subset='name').copy()

    def _load_history(self):
        """Load game history from file if it exists."""
        if os.path.exists('game_history.json'):
            with open('game_history.json', 'r') as f:
                data = json.load(f)
                self.game_history = data.get('history', [])
                self.score = data.get('score', {'ai_wins': 0, 'user_wins': 0})

    def _save_history(self):
        """Save game history to file."""
        with open('game_history.json', 'w') as f:
            json.dump({
                'score': self.score,
                'history': self.game_history
            }, f, indent=2)

    # ═══════════════════════════════════════════════════════════════════════
    # MODE 1: AI GUESSES (User thinks, AI asks questions)
    # ═══════════════════════════════════════════════════════════════════════

    def start_ai_guesses_mode(self):
        """Initialize a new game where AI asks questions to guess."""
        self.current_game = {
            'mode': 'ai_guesses',
            'answers': {},           # feature -> 0 or 1
            'asked_features': [],    # features already asked
            'candidates': self.unique_entities.copy(),
            'question_count': 0,
            'max_questions': 20,
            'confidence': 0.0,
            'started_at': datetime.now().isoformat(),
        }
        return self.current_game

    def get_next_question(self):
        """
        Use Decision Tree (Exp-4) feature importance + information gain
        to pick the BEST next question that splits candidates most evenly.
        """
        if not self.current_game or self.current_game['question_count'] >= 20:
            return None

        candidates = self.current_game['candidates']
        asked = set(self.current_game['asked_features'])
        available_features = [f for f in self.feature_cols if f not in asked]

        if not available_features or len(candidates) <= 1:
            return None

        # Pick the feature that best splits the remaining candidates
        best_feature = None
        best_score = -1

        for feat in available_features:
            if feat not in candidates.columns:
                continue
            # Information gain heuristic: pick feature closest to 50/50 split
            ones = candidates[feat].sum()
            zeros = len(candidates) - ones
            total = len(candidates)
            if total == 0:
                continue
            # Entropy-based score: balanced split is best
            p = ones / total
            if p == 0 or p == 1:
                score = 0
            else:
                score = -p * np.log2(p) - (1 - p) * np.log2(1 - p)

            # Boost score by Decision Tree feature importance
            feat_idx = self.feature_cols.index(feat) if feat in self.feature_cols else -1
            if feat_idx >= 0:
                importance = self.models['dt'].feature_importances_[feat_idx]
                score *= (1 + importance)

            if score > best_score:
                best_score = score
                best_feature = feat

        if best_feature is None:
            best_feature = available_features[0]

        question_text = self.QUESTION_MAP.get(best_feature, f"Is '{best_feature}' true?")

        return {
            'feature': best_feature,
            'question': question_text,
            'question_number': self.current_game['question_count'] + 1,
            'candidates_remaining': len(candidates),
        }

    def answer_question(self, feature, answer):
        """
        Process user's YES/NO answer and narrow candidates.
        Returns updated game state with confidence.
        """
        if isinstance(answer, str):
            answer_val = 1 if answer.lower() in ('yes', 'true', '1', 'y') else 0
        else:
            answer_val = 1 if answer else 0
        self.current_game['answers'][feature] = answer_val
        self.current_game['asked_features'].append(feature)
        self.current_game['question_count'] += 1

        # Narrow down candidates based on the answer
        candidates = self.current_game['candidates']
        if feature in candidates.columns:
            self.current_game['candidates'] = candidates[
                candidates[feature] == answer_val
            ].copy()

        # If no candidates match, keep all (fuzzy matching)
        if len(self.current_game['candidates']) == 0:
            self.current_game['candidates'] = candidates.copy()

        # Calculate confidence using Naive Bayes (Exp-9)
        confidence = self._calculate_confidence()
        self.current_game['confidence'] = confidence

        # Get current top guesses from all models
        top_guesses = self._get_predictions()

        return {
            'confidence': confidence,
            'candidates_remaining': len(self.current_game['candidates']),
            'question_count': self.current_game['question_count'],
            'top_guesses': top_guesses,
            'should_guess': (
                (len(self.current_game['candidates']) <= 1)
                or (self.current_game['question_count'] >= 20)
                or (len(self.current_game['candidates']) <= 3 and self.current_game['question_count'] >= 12)
            ),
        }

    def _calculate_confidence(self):
        """Calculate confidence based on how much the candidate pool has been narrowed."""
        candidates_left = len(self.current_game['candidates'])
        total = len(self.unique_entities)
        if total == 0:
            return 0.0
        # 0% when no candidates eliminated, grows toward 99.9% as pool narrows
        confidence = (1 - candidates_left / total) * 100
        return min(round(confidence, 1), 99.9)

    def _get_predictions(self):
        """Get prediction from Decision Tree model."""
        if not self.current_game['answers']:
            return []

        feature_vector = np.zeros(len(self.feature_cols))
        candidates = self.current_game.get('candidates')
        
        for feat in self.feature_cols:
            idx = self.feature_cols.index(feat)
            if feat in self.current_game['answers']:
                feature_vector[idx] = self.current_game['answers'][feat]
            else:
                # Impute missing feature with the mode of remaining candidates
                if candidates is not None and not candidates.empty:
                    mode_val = candidates[feat].mode()
                    if not mode_val.empty:
                        feature_vector[idx] = mode_val.iloc[0]
                else:
                    feature_vector[idx] = 0

        predictions = {}
        try:
            pred = self.models['dt'].predict([feature_vector])[0]
            name = self.le_name.inverse_transform([pred])[0]
            predictions['Decision Tree'] = name
        except Exception:
            pass

        return predictions

    def make_guess(self):
        """AI makes its final guess using ensemble of models."""
        candidates = self.current_game['candidates']

        # If only one candidate left, that's the answer
        if len(candidates) == 1:
            guess = candidates.iloc[0]['name']
            model_used = "Candidate Elimination"
        elif len(candidates) > 0:
            # Use Decision Tree prediction
            preds = self._get_predictions()
            candidate_names = set(candidates['name'].values)
            if 'Decision Tree' in preds and preds['Decision Tree'] in candidate_names:
                guess = preds['Decision Tree']
                model_used = 'Decision Tree'
            else:
                # Fallback to most common name in candidates
                guess = candidates['name'].mode().iloc[0]
                model_used = "Candidate Mode"
        else:
            preds = self._get_predictions()
            guess = preds.get('Random Forest', preds.get('Decision Tree', 'Unknown'))
            model_used = "Model Ensemble"

        return {
            'guess': guess,
            'model_used': model_used,
            'confidence': self.current_game['confidence'],
            'questions_asked': self.current_game['question_count'],
            'all_predictions': self._get_predictions(),
        }

    def finalize_ai_guess(self, correct):
        """Record the result of AI's guess."""
        result = {
            'mode': 'ai_guesses',
            'timestamp': datetime.now().isoformat(),
            'questions_asked': self.current_game['question_count'],
            'ai_correct': correct,
            'confidence': self.current_game['confidence'],
        }
        if correct:
            self.score['ai_wins'] += 1
        else:
            self.score['user_wins'] += 1

        self.game_history.append(result)
        self._save_history()
        return self.score

    # ═══════════════════════════════════════════════════════════════════════
    # MODE 2: USER GUESSES (AI picks object, user asks questions)
    # ═══════════════════════════════════════════════════════════════════════

    def start_user_guesses_mode(self):
        """AI secretly picks a random object."""
        secret = self.unique_entities.sample(1, random_state=None).iloc[0]
        self.current_game = {
            'mode': 'user_guesses',
            'secret_name': secret['name'],
            'secret_category': secret['category'],
            'secret_features': {col: int(secret[col])
                                for col in self.feature_cols},
            'questions_asked': [],
            'question_count': 0,
            'max_questions': 20,
            'hints_used': 0,
            'score_penalty': 0,
            'started_at': datetime.now().isoformat(),
        }
        return {
            'message': "I've picked something! Ask me YES/NO questions to guess what it is.",
            'category': secret['category'],
        }

    def answer_user_question(self, question_text):
        """
        AI answers user's question about the secret object.
        Maps natural language question to features.
        """
        question_lower = question_text.lower().strip()
        secret = self.current_game['secret_features']

        # Try to match question to features
        answer = None
        matched_feature = None

        # Keyword matching for each feature
        keyword_map = {
            'is_alive': ['alive', 'living', 'life'],
            'is_animal': ['animal', 'creature', 'beast'],
            'is_human': ['human', 'person', 'people', 'man', 'woman'],
            'is_plant': ['plant', 'tree', 'flower', 'vegetation', 'grow in soil'],
            'is_object': ['object', 'thing', 'inanimate', 'non-living', 'man-made'],
            'has_wings': ['wing', 'wings'],
            'can_fly': ['fly', 'flying', 'airborne'],
            'lives_in_water': ['water', 'swim', 'ocean', 'sea', 'lake', 'river', 'aquatic'],
            'lives_in_jungle': ['jungle', 'forest', 'woods', 'wild'],
            'lives_in_desert': ['desert', 'sand', 'arid'],
            'lives_in_home': ['home', 'house', 'indoor', 'inside', 'domestic'],
            'is_big': ['big', 'large', 'huge', 'giant', 'bigger than'],
            'is_small': ['small', 'tiny', 'little', 'miniature', 'smaller than'],
            'has_4_legs': ['4 legs', 'four legs', 'quadruped'],
            'has_2_legs': ['2 legs', 'two legs', 'biped', 'walk upright'],
            'has_no_legs': ['no legs', 'legless'],
            'has_fur': ['fur', 'furry', 'hairy', 'hair'],
            'has_scales': ['scale', 'scales', 'scaly'],
            'has_feathers': ['feather', 'feathers', 'plumage'],
            'has_shell': ['shell', 'hard covering', 'exoskeleton'],
            'is_carnivore': ['carnivore', 'meat', 'predator', 'hunt', 'eat meat'],
            'is_herbivore': ['herbivore', 'plant-eater', 'eat plants', 'vegetarian', 'eat grass'],
            'is_omnivore': ['omnivore', 'eat everything', 'eat both'],
            'is_dangerous': ['dangerous', 'deadly', 'lethal', 'harm', 'kill', 'attack'],
            'is_domestic': ['domestic', 'tame', 'pet', 'kept by humans'],
            'is_nocturnal': ['nocturnal', 'night', 'active at night'],
            'found_in_africa': ['africa', 'african', 'savanna', 'serengeti'],
            'found_in_asia': ['asia', 'asian', 'india', 'china', 'japan'],
            'found_in_ocean': ['ocean', 'marine', 'deep sea'],
            'is_fast': ['fast', 'quick', 'speed', 'rapid'],
            'is_colorful': ['color', 'colour', 'colorful', 'colourful', 'bright'],
            'makes_sound': ['sound', 'noise', 'loud', 'call', 'roar', 'bark', 'sing'],
            'can_be_pet': ['pet', 'companion'],
            'is_extinct': ['extinct', 'dinosaur', 'no longer alive', 'dead species'],
            'is_fictional': ['fictional', 'myth', 'fantasy', 'imaginary', 'fairy tale', 'legend'],
            'is_used_daily': ['daily', 'everyday', 'common', 'regular use'],
            'is_electronic': ['electronic', 'electric', 'battery', 'plug in', 'digital'],
            'is_food_related': ['food', 'eat', 'cook', 'kitchen', 'edible'],
            'is_vehicle': ['vehicle', 'transport', 'drive', 'ride', 'car', 'travel'],
            'is_used_in_sports': ['sport', 'game', 'play', 'athletic', 'exercise'],
        }

        for feature, keywords in keyword_map.items():
            if any(kw in question_lower for kw in keywords):
                matched_feature = feature
                answer = bool(secret.get(feature, 0))
                break

        if answer is None:
            # Default: couldn't match the question
            return {
                'answer': "I'm not sure about that. Try asking differently!",
                'understood': False,
                'question_count': self.current_game['question_count'],
            }

        self.current_game['question_count'] += 1
        self.current_game['questions_asked'].append({
            'question': question_text,
            'feature': matched_feature,
            'answer': answer,
        })

        return {
            'answer': 'YES' if answer else 'NO',
            'understood': True,
            'feature': matched_feature,
            'question_count': self.current_game['question_count'],
            'questions_remaining': 20 - self.current_game['question_count'],
        }

    def get_hint(self):
        """Give user a hint about the secret object (-5 points)."""
        self.current_game['hints_used'] += 1
        self.current_game['score_penalty'] += 5

        secret = self.current_game['secret_features']
        category = self.current_game['secret_category']
        name = self.current_game['secret_name']

        hints = [
            f"It belongs to the '{category}' category.",
            f"The first letter is '{name[0]}'.",
            f"It has {len(name)} letters in its name.",
        ]

        hint_idx = min(self.current_game['hints_used'] - 1, len(hints) - 1)
        return {
            'hint': hints[hint_idx],
            'penalty': 5,
            'total_penalty': self.current_game['score_penalty'],
        }

    def check_user_guess(self, guess):
        """Check if user's guess is correct."""
        secret = self.current_game['secret_name']
        correct = guess.strip().lower() == secret.lower()

        result = {
            'correct': correct,
            'secret': secret,
            'category': self.current_game['secret_category'],
            'questions_asked': self.current_game['question_count'],
            'hints_used': self.current_game['hints_used'],
        }

        if correct:
            self.score['user_wins'] += 1
        else:
            self.score['ai_wins'] += 1

        self.game_history.append({
            'mode': 'user_guesses',
            'timestamp': datetime.now().isoformat(),
            'secret': secret,
            'user_guess': guess,
            'correct': correct,
            'questions_asked': self.current_game['question_count'],
            'hints_used': self.current_game['hints_used'],
        })
        self._save_history()

        return result

    def give_up(self):
        """User gives up — reveal the answer."""
        self.score['ai_wins'] += 1
        secret = self.current_game['secret_name']

        self.game_history.append({
            'mode': 'user_guesses',
            'timestamp': datetime.now().isoformat(),
            'secret': secret,
            'user_guess': None,
            'correct': False,
            'gave_up': True,
            'questions_asked': self.current_game['question_count'],
        })
        self._save_history()

        return {
            'secret': secret,
            'category': self.current_game['secret_category'],
        }

    # ═══════════════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═══════════════════════════════════════════════════════════════════════

    def get_score(self):
        """Return current scoreboard."""
        return self.score

    def get_stats(self):
        """Return game statistics."""
        total = len(self.game_history)
        return {
            'total_games': total,
            'ai_wins': self.score['ai_wins'],
            'user_wins': self.score['user_wins'],
            'history': self.game_history[-10:],  # last 10 games
        }

    def get_candidates_list(self):
        """Return current candidates in AI guesses mode."""
        if not self.current_game or self.current_game['mode'] != 'ai_guesses':
            return []
        return self.current_game['candidates']['name'].unique().tolist()
