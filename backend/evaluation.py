"""
evaluation.py — Evaluation & Report Generation for AI Mind Reader
# Exp-2: Feature Engineering — Feature importance visualization
# Exp-4: Decision Tree — Confusion matrix
# Exp-6: KNN, Exp-9: Naive Bayes, Exp-10: AdaBoost/GradientBoost, Exp-11: Random Forest
# Exp-12: Full project integration — Evaluation & reporting

Generates:
- Accuracy comparison bar chart
- Confusion matrix heatmap for Decision Tree
- Feature importance chart
- Learning curve
- project_report.txt
"""

import pandas as pd
import numpy as np
import json
import os
import warnings
warnings.filterwarnings('ignore')

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, learning_curve
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix, accuracy_score
import joblib

# ── Setup ────────────────────────────────────────────────────────────────
os.makedirs('plots', exist_ok=True)
os.makedirs('static', exist_ok=True)  # Also save to static for web display

print("=" * 60)
print("📊 AI Mind Reader — Evaluation & Report Generator")
print("=" * 60)

# ═══════════════════════════════════════════════════════════════════════════
# LOAD DATA & MODELS
# ═══════════════════════════════════════════════════════════════════════════
print("\n📂 Loading data and models...")
df = pd.read_csv('mindreader_data.csv')
feature_cols = joblib.load('models/feature_cols.pkl')
le_name = joblib.load('models/label_encoder_name.pkl')

# Load accuracies
with open('model_accuracy.json', 'r') as f:
    accuracies = json.load(f)

# Prepare data
X = df[feature_cols].values
le = LabelEncoder()
y = le.fit_transform(df['name'])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"   Dataset: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"   Features: {len(feature_cols)}")

# ═══════════════════════════════════════════════════════════════════════════
# PLOT 1: Accuracy Comparison Bar Chart
# ═══════════════════════════════════════════════════════════════════════════
print("\n📊 Generating accuracy comparison chart...")

fig, ax = plt.subplots(figsize=(12, 6))
models = list(accuracies.keys())
accs = list(accuracies.values())

colors = ['#00ff41', '#0ff', '#f0f', '#ff0', '#f90', '#f44', '#66f']
bars = ax.bar(models, accs, color=colors[:len(models)], edgecolor='white', linewidth=0.5)

# Add value labels on bars
for bar, acc in zip(bars, accs):
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
            f'{acc}%', ha='center', va='bottom', fontweight='bold',
            color='white', fontsize=10)

ax.set_ylabel('Accuracy (%)', color='white', fontsize=12)
ax.set_title('Model Accuracy Comparison — AI Mind Reader', color='#0ff',
             fontsize=14, fontweight='bold')
ax.set_ylim(0, 105)
ax.set_facecolor('#1a1a1a')
fig.patch.set_facecolor('#0a0a0a')
ax.tick_params(colors='white')
ax.spines['bottom'].set_color('#333')
ax.spines['left'].set_color('#333')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.xticks(rotation=30, ha='right')
plt.tight_layout()

plt.savefig('plots/accuracy_comparison.png', dpi=150, bbox_inches='tight',
            facecolor='#0a0a0a')
plt.savefig('static/accuracy_comparison.png', dpi=150, bbox_inches='tight',
            facecolor='#0a0a0a')
plt.close()
print("   ✅ Saved: plots/accuracy_comparison.png")

# ═══════════════════════════════════════════════════════════════════════════
# PLOT 2: Confusion Matrix Heatmap (Decision Tree)
# ═══════════════════════════════════════════════════════════════════════════
print("\n📊 Generating confusion matrix heatmap...")

# Retrain DT for confusion matrix (or load saved)
dt_model = joblib.load('models/dt_model.pkl')
y_pred = dt_model.predict(X_test)

# For readability, show category-level confusion
le_cat = LabelEncoder()
y_cat = le_cat.fit_transform(df['category'])
_, X_test_cat, _, y_test_cat = train_test_split(X, y_cat, test_size=0.2, random_state=42)

dt_cat = DecisionTreeClassifier(criterion='entropy', max_depth=10, random_state=42)
dt_cat.fit(X_train, y_cat[:len(X_train)])
y_cat_pred = dt_cat.predict(X_test_cat)
cm = confusion_matrix(y_test_cat, y_cat_pred)

fig, ax = plt.subplots(figsize=(8, 6))
cat_labels = le_cat.classes_
sns.heatmap(cm, annot=True, fmt='d', cmap='YlGn',
            xticklabels=cat_labels, yticklabels=cat_labels,
            linewidths=0.5, linecolor='#333', ax=ax,
            cbar_kws={'label': 'Count'})
ax.set_xlabel('Predicted Category', color='white', fontsize=12)
ax.set_ylabel('Actual Category', color='white', fontsize=12)
ax.set_title('Confusion Matrix — Decision Tree (Category Level)', color='#0ff',
             fontsize=13, fontweight='bold')
ax.set_facecolor('#1a1a1a')
fig.patch.set_facecolor('#0a0a0a')
ax.tick_params(colors='white')

plt.tight_layout()
plt.savefig('plots/confusion_matrix.png', dpi=150, bbox_inches='tight',
            facecolor='#0a0a0a')
plt.savefig('static/confusion_matrix.png', dpi=150, bbox_inches='tight',
            facecolor='#0a0a0a')
plt.close()
print("   ✅ Saved: plots/confusion_matrix.png")

# ═══════════════════════════════════════════════════════════════════════════
# PLOT 3: Feature Importance Chart
# ═══════════════════════════════════════════════════════════════════════════
print("\n📊 Generating feature importance chart...")

feat_imp = joblib.load('models/feature_importance_named.pkl')
top_n = 20
top_features = feat_imp[:top_n]
feat_names = [f[0] for f in top_features][::-1]
feat_vals = [f[1] for f in top_features][::-1]

fig, ax = plt.subplots(figsize=(10, 8))
colors_fi = plt.cm.YlGn(np.linspace(0.3, 0.9, len(feat_names)))
ax.barh(feat_names, feat_vals, color=colors_fi, edgecolor='white', linewidth=0.3)

ax.set_xlabel('Importance Score', color='white', fontsize=12)
ax.set_title(f'Top {top_n} Feature Importance — Decision Tree', color='#0ff',
             fontsize=13, fontweight='bold')
ax.set_facecolor('#1a1a1a')
fig.patch.set_facecolor('#0a0a0a')
ax.tick_params(colors='white')
ax.spines['bottom'].set_color('#333')
ax.spines['left'].set_color('#333')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('plots/feature_importance.png', dpi=150, bbox_inches='tight',
            facecolor='#0a0a0a')
plt.savefig('static/feature_importance.png', dpi=150, bbox_inches='tight',
            facecolor='#0a0a0a')
plt.close()
print("   ✅ Saved: plots/feature_importance.png")

# ═══════════════════════════════════════════════════════════════════════════
# PLOT 4: Learning Curve
# ═══════════════════════════════════════════════════════════════════════════
print("\n📊 Generating learning curve...")

dt_lc = DecisionTreeClassifier(criterion='entropy', max_depth=15, random_state=42)
train_sizes, train_scores, val_scores = learning_curve(
    dt_lc, X, y, cv=5, scoring='accuracy',
    train_sizes=np.linspace(0.1, 1.0, 10),
    n_jobs=-1
)

train_mean = train_scores.mean(axis=1)
train_std = train_scores.std(axis=1)
val_mean = val_scores.mean(axis=1)
val_std = val_scores.std(axis=1)

fig, ax = plt.subplots(figsize=(10, 6))
ax.fill_between(train_sizes, train_mean - train_std, train_mean + train_std,
                alpha=0.1, color='#00ff41')
ax.fill_between(train_sizes, val_mean - val_std, val_mean + val_std,
                alpha=0.1, color='#0ff')
ax.plot(train_sizes, train_mean, 'o-', color='#00ff41', label='Training Score', linewidth=2)
ax.plot(train_sizes, val_mean, 'o-', color='#0ff', label='Validation Score', linewidth=2)

ax.set_xlabel('Training Set Size', color='white', fontsize=12)
ax.set_ylabel('Accuracy', color='white', fontsize=12)
ax.set_title('Learning Curve — Decision Tree', color='#0ff',
             fontsize=13, fontweight='bold')
ax.legend(facecolor='#1a1a1a', edgecolor='#333', labelcolor='white')
ax.set_facecolor('#1a1a1a')
fig.patch.set_facecolor('#0a0a0a')
ax.tick_params(colors='white')
ax.spines['bottom'].set_color('#333')
ax.spines['left'].set_color('#333')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, alpha=0.1)

plt.tight_layout()
plt.savefig('plots/learning_curve.png', dpi=150, bbox_inches='tight',
            facecolor='#0a0a0a')
plt.savefig('static/learning_curve.png', dpi=150, bbox_inches='tight',
            facecolor='#0a0a0a')
plt.close()
print("   ✅ Saved: plots/learning_curve.png")

# ═══════════════════════════════════════════════════════════════════════════
# PLOT 5: Category Distribution
# ═══════════════════════════════════════════════════════════════════════════
print("\n📊 Generating category distribution chart...")

fig, ax = plt.subplots(figsize=(8, 8))
cat_counts = df['category'].value_counts()
colors_pie = ['#00ff41', '#0ff', '#f0f', '#ff0', '#f90']
explode = [0.05] * len(cat_counts)

wedges, texts, autotexts = ax.pie(
    cat_counts.values, labels=cat_counts.index, colors=colors_pie[:len(cat_counts)],
    explode=explode, autopct='%1.1f%%', startangle=140,
    textprops={'color': 'white', 'fontsize': 12}
)
for autotext in autotexts:
    autotext.set_fontweight('bold')

ax.set_title('Dataset Category Distribution', color='#0ff',
             fontsize=14, fontweight='bold')
fig.patch.set_facecolor('#0a0a0a')

plt.tight_layout()
plt.savefig('plots/category_distribution.png', dpi=150, bbox_inches='tight',
            facecolor='#0a0a0a')
plt.savefig('static/category_distribution.png', dpi=150, bbox_inches='tight',
            facecolor='#0a0a0a')
plt.close()
print("   ✅ Saved: plots/category_distribution.png")

# ═══════════════════════════════════════════════════════════════════════════
# GENERATE PROJECT REPORT
# ═══════════════════════════════════════════════════════════════════════════
print("\n📝 Generating project report...")

best_model = max(accuracies, key=accuracies.get)
best_acc = accuracies[best_model]

# Load game history stats
game_stats = {'total': 0, 'ai_wins': 0, 'user_wins': 0}
if os.path.exists('game_history.json'):
    with open('game_history.json', 'r') as f:
        history = json.load(f)
        game_stats['total'] = len(history.get('history', []))
        game_stats['ai_wins'] = history.get('score', {}).get('ai_wins', 0)
        game_stats['user_wins'] = history.get('score', {}).get('user_wins', 0)

report = f"""
{'='*60}
    AI MIND READER — PROJECT REPORT
{'='*60}

Generated automatically by evaluation.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 DATASET DESCRIPTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Rows:         {df.shape[0]}
  Total Columns:      {df.shape[1]}
  Feature Columns:    {len(feature_cols)}
  Unique Entities:    {df['name'].nunique()}
  
  Category Distribution:
{chr(10).join(f'    - {cat}: {count} rows' for cat, count in df['category'].value_counts().items())}

  Features Used:
{chr(10).join(f'    {i+1:2d}. {col}' for i, col in enumerate(feature_cols))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧠 MODELS USED AND ACCURACIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{chr(10).join(f'  {name:35s} {acc:6.2f}%' for name, acc in sorted(accuracies.items(), key=lambda x: x[1], reverse=True))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 BEST PERFORMING MODEL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Model:    {best_model}
  Accuracy: {best_acc}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 GAME STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Games Played: {game_stats['total']}
  AI Wins:            {game_stats['ai_wins']}
  User Wins:          {game_stats['user_wins']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎓 LAB EXPERIMENTS COVERED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Exp-1:  Python, NumPy, Pandas — Data generation & loading
  Exp-2:  Feature Engineering — Preprocessing & importance
  Exp-3:  Linear/Multiple Regression — Confidence scoring
  Exp-4:  Decision Tree ID3 — Main brain of the game
  Exp-5:  Logistic Regression — Question selection probability
  Exp-6:  KNN — Backup guesser
  Exp-7:  K-Means — Object clustering
  Exp-8:  Agglomerative Clustering — Category grouping
  Exp-9:  Naive Bayes — Confidence percentage
  Exp-10: AdaBoost + Gradient Boost — Strong learners
  Exp-11: Random Forest — Final predictor
  Exp-12: Full project integration — Complete system

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 EVALUATION PLOTS GENERATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. plots/accuracy_comparison.png
  2. plots/confusion_matrix.png
  3. plots/feature_importance.png
  4. plots/learning_curve.png
  5. plots/category_distribution.png

{'='*60}
  AI Mind Reader — Lab Project
  All 12 Experiments Covered ✅
{'='*60}
"""

with open('project_report.txt', 'w', encoding='utf-8') as f:
    f.write(report)
print("   ✅ Saved: project_report.txt")

# Print report to console
print(report)

print("\n" + "=" * 60)
print("✅ EVALUATION COMPLETE!")
print("=" * 60)
print("\nGenerated files:")
print("   📊 plots/accuracy_comparison.png")
print("   📊 plots/confusion_matrix.png")
print("   📊 plots/feature_importance.png")
print("   📊 plots/learning_curve.png")
print("   📊 plots/category_distribution.png")
print("   📝 project_report.txt")
