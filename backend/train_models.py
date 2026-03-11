"""
train_models.py — Train All ML Models for AI Mind Reader
# Exp-1: Python, NumPy, Pandas — Data loading
# Exp-2: Feature Engineering — Preprocessing & feature importance
# Exp-3: Linear/Multiple Regression — Confidence scoring  
# Exp-4: Decision Tree ID3 — Main brain of the game
# Exp-5: Logistic Regression — Question selection probability
# Exp-6: KNN — Backup guesser
# Exp-7: K-Means — Object clustering
# Exp-8: Agglomerative Clustering — Category grouping
# Exp-9: Naive Bayes — Confidence percentage
# Exp-10: AdaBoost + Gradient Boost — Strong learners
# Exp-11: Random Forest — Final predictor
# Exp-12: Full project integration
"""

import pandas as pd
import numpy as np
import json
import os
import warnings
warnings.filterwarnings('ignore')

# Exp-1: Python, NumPy, Pandas
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Exp-4: Decision Tree
from sklearn.tree import DecisionTreeClassifier

# Exp-5: Logistic Regression
from sklearn.linear_model import LogisticRegression

# Exp-6: KNN
from sklearn.neighbors import KNeighborsClassifier

# Exp-7: K-Means Clustering
from sklearn.cluster import KMeans

# Exp-8: Agglomerative Clustering
from sklearn.cluster import AgglomerativeClustering

# Exp-9: Naive Bayes
from sklearn.naive_bayes import GaussianNB

# Exp-10: AdaBoost + Gradient Boost
from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier

# Exp-11: Random Forest
from sklearn.ensemble import RandomForestClassifier

# Exp-3: Linear Regression for confidence
from sklearn.linear_model import LinearRegression

from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix)
import joblib

# ── Create models directory ─────────────────────────────────────────────
os.makedirs('models', exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════
# STEP 1: LOAD DATA (Exp-1)
# ═══════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("📂 STEP 1: Loading Dataset...")
print("=" * 60)

df = pd.read_csv('mindreader_data.csv')
print(f"   Rows: {df.shape[0]}, Columns: {df.shape[1]}")
print(f"   Categories: {df['category'].value_counts().to_dict()}")

# ═══════════════════════════════════════════════════════════════════════════
# STEP 2: FEATURE ENGINEERING (Exp-2)
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("🔧 STEP 2: Feature Engineering (Exp-2)...")
print("=" * 60)

# Handle missing values
print(f"\n   Missing values before: {df.isnull().sum().sum()}")
df = df.fillna(0)
print(f"   Missing values after:  {df.isnull().sum().sum()}")

# Encode target variable (name)
le_name = LabelEncoder()
df['name_encoded'] = le_name.fit_transform(df['name'])

# Encode category
le_category = LabelEncoder()
df['category_encoded'] = le_category.fit_transform(df['category'])

# Define feature columns (binary features only)
feature_cols = [col for col in df.columns 
                if col not in ['name', 'category', 'name_encoded', 'category_encoded']]

X = df[feature_cols].values
y_name = df['name_encoded'].values
y_category = df['category_encoded'].values

print(f"\n   Feature columns ({len(feature_cols)}):")
for i, col in enumerate(feature_cols):
    print(f"      {i+1}. {col}")

# ═══════════════════════════════════════════════════════════════════════════
# STEP 3: TRAIN/TEST SPLIT
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("✂️  STEP 3: Splitting Data...")
print("=" * 60)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_name, test_size=0.2, random_state=42, stratify=None
)
_, _, y_cat_train, y_cat_test = train_test_split(
    X, y_category, test_size=0.2, random_state=42
)

print(f"   Training set: {X_train.shape[0]} samples")
print(f"   Test set:     {X_test.shape[0]} samples")

# ═══════════════════════════════════════════════════════════════════════════
# STEP 4: TRAIN ALL MODELS
# ═══════════════════════════════════════════════════════════════════════════
accuracies = {}

# ── 4a) Decision Tree ID3 (Exp-4) — MAIN BRAIN ──────────────────────────
print("\n" + "=" * 60)
print("🌳 Training Decision Tree (ID3) — Exp-4 — MAIN BRAIN")
print("=" * 60)
dt_model = DecisionTreeClassifier(
    criterion='entropy',  # ID3 uses entropy / information gain
    max_depth=20,
    min_samples_split=2,
    random_state=42
)
dt_model.fit(X_train, y_train)
dt_pred = dt_model.predict(X_test)
dt_acc = accuracy_score(y_test, dt_pred)
accuracies['Decision Tree (ID3)'] = round(dt_acc * 100, 2)
print(f"   ✅ Accuracy: {dt_acc * 100:.2f}%")

# Print feature importance (Exp-2)
print("\n   📊 Feature Importance (Top 10):")
importance = dt_model.feature_importances_
feat_imp = sorted(zip(feature_cols, importance), key=lambda x: x[1], reverse=True)
for feat, imp in feat_imp[:10]:
    bar = "█" * int(imp * 50)
    print(f"      {feat:20s} {imp:.4f} {bar}")

# Classification Report & Confusion Matrix
print("\n   📋 Classification Report (Decision Tree):")
print(classification_report(y_test, dt_pred, zero_division=0,
                            output_dict=False))
print("   🔲 Confusion Matrix saved (see evaluation.py for heatmap)")

joblib.dump(dt_model, 'models/dt_model.pkl')
print("   💾 Saved: models/dt_model.pkl")

# ── 4b) KNN Classifier (Exp-6) — Backup Guesser ────────────────────────
print("\n" + "=" * 60)
print("📍 Training KNN Classifier — Exp-6 — Backup Guesser")
print("=" * 60)
knn_model = KNeighborsClassifier(n_neighbors=5, metric='hamming')
knn_model.fit(X_train, y_train)
knn_pred = knn_model.predict(X_test)
knn_acc = accuracy_score(y_test, knn_pred)
accuracies['KNN'] = round(knn_acc * 100, 2)
print(f"   ✅ Accuracy: {knn_acc * 100:.2f}%")
joblib.dump(knn_model, 'models/knn_model.pkl')
print("   💾 Saved: models/knn_model.pkl")

# ── 4c) Naive Bayes (Exp-9) — Confidence Scoring ────────────────────────
print("\n" + "=" * 60)
print("📊 Training Naive Bayes — Exp-9 — Confidence Scoring")
print("=" * 60)
nb_model = GaussianNB()
nb_model.fit(X_train, y_train)
nb_pred = nb_model.predict(X_test)
nb_acc = accuracy_score(y_test, nb_pred)
accuracies['Naive Bayes'] = round(nb_acc * 100, 2)
print(f"   ✅ Accuracy: {nb_acc * 100:.2f}%")
joblib.dump(nb_model, 'models/nb_model.pkl')
print("   💾 Saved: models/nb_model.pkl")

# ── 4d) AdaBoost (Exp-10) — Strong Learner ──────────────────────────────
print("\n" + "=" * 60)
print("⚡ Training AdaBoost — Exp-10 — Strong Learner")
print("=" * 60)
ada_model = AdaBoostClassifier(
    n_estimators=100,
    random_state=42,
    algorithm='SAMME'
)
ada_model.fit(X_train, y_train)
ada_pred = ada_model.predict(X_test)
ada_acc = accuracy_score(y_test, ada_pred)
accuracies['AdaBoost'] = round(ada_acc * 100, 2)
print(f"   ✅ Accuracy: {ada_acc * 100:.2f}%")
joblib.dump(ada_model, 'models/ada_model.pkl')
print("   💾 Saved: models/ada_model.pkl")

# ── 4e) Gradient Boost (Exp-10) — Strong Learner ────────────────────────
print("\n" + "=" * 60)
print("🚀 Training Gradient Boost — Exp-10 — Strong Learner")
print("=" * 60)
gb_model = GradientBoostingClassifier(
    n_estimators=100,
    max_depth=5,
    random_state=42
)
gb_model.fit(X_train, y_train)
gb_pred = gb_model.predict(X_test)
gb_acc = accuracy_score(y_test, gb_pred)
accuracies['Gradient Boost'] = round(gb_acc * 100, 2)
print(f"   ✅ Accuracy: {gb_acc * 100:.2f}%")
joblib.dump(gb_model, 'models/gb_model.pkl')
print("   💾 Saved: models/gb_model.pkl")

# ── 4f) Random Forest (Exp-11) — Final Predictor ────────────────────────
print("\n" + "=" * 60)
print("🌲 Training Random Forest — Exp-11 — Final Predictor")
print("=" * 60)
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)
rf_acc = accuracy_score(y_test, rf_pred)
accuracies['Random Forest'] = round(rf_acc * 100, 2)
print(f"   ✅ Accuracy: {rf_acc * 100:.2f}%")
joblib.dump(rf_model, 'models/rf_model.pkl')
print("   💾 Saved: models/rf_model.pkl")

# ═══════════════════════════════════════════════════════════════════════════
# ADDITIONAL: Logistic Regression (Exp-5) — Question Selection
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("📈 Training Logistic Regression — Exp-5 — Question Selection")
print("=" * 60)
lr_model = LogisticRegression(max_iter=1000, random_state=42)
lr_model.fit(X_train, y_cat_train)
lr_pred = lr_model.predict(X_test)
lr_acc = accuracy_score(y_cat_test, lr_pred)
accuracies['Logistic Regression (category)'] = round(lr_acc * 100, 2)
print(f"   ✅ Category prediction accuracy: {lr_acc * 100:.2f}%")
joblib.dump(lr_model, 'models/lr_model.pkl')
print("   💾 Saved: models/lr_model.pkl")

# ═══════════════════════════════════════════════════════════════════════════
# ADDITIONAL: Linear Regression (Exp-3) — Confidence Scoring
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("📉 Training Linear Regression — Exp-3 — Confidence Scoring")
print("=" * 60)
lin_model = LinearRegression()
lin_model.fit(X_train, y_train)
lin_pred = lin_model.predict(X_test)
print(f"   ✅ R² Score: {lin_model.score(X_test, y_test):.4f}")
joblib.dump(lin_model, 'models/lin_model.pkl')
print("   💾 Saved: models/lin_model.pkl")

# ═══════════════════════════════════════════════════════════════════════════
# ADDITIONAL: K-Means Clustering (Exp-7) — Object Clustering
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("🔵 K-Means Clustering — Exp-7 — Object Clustering")
print("=" * 60)
kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
cluster_labels = kmeans.fit_predict(X)
print(f"   ✅ Clusters formed: {len(set(cluster_labels))}")
print(f"   Cluster distribution: {dict(zip(*np.unique(cluster_labels, return_counts=True)))}")
joblib.dump(kmeans, 'models/kmeans_model.pkl')
print("   💾 Saved: models/kmeans_model.pkl")

# ═══════════════════════════════════════════════════════════════════════════
# ADDITIONAL: Agglomerative Clustering (Exp-8) — Category Grouping
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("🔗 Agglomerative Clustering — Exp-8 — Category Grouping")
print("=" * 60)
agg_model = AgglomerativeClustering(n_clusters=5)
agg_labels = agg_model.fit_predict(X)
print(f"   ✅ Clusters formed: {len(set(agg_labels))}")
print(f"   Cluster distribution: {dict(zip(*np.unique(agg_labels, return_counts=True)))}")

# ═══════════════════════════════════════════════════════════════════════════
# SAVE ENCODERS & METADATA
# ═══════════════════════════════════════════════════════════════════════════
joblib.dump(le_name, 'models/label_encoder_name.pkl')
joblib.dump(le_category, 'models/label_encoder_category.pkl')
joblib.dump(feature_cols, 'models/feature_cols.pkl')

# ═══════════════════════════════════════════════════════════════════════════
# SAVE ACCURACY REPORT
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("📊 MODEL ACCURACY SUMMARY")
print("=" * 60)
for model_name, acc in sorted(accuracies.items(), key=lambda x: x[1], reverse=True):
    bar = "█" * int(acc / 2)
    print(f"   {model_name:35s} {acc:6.2f}% {bar}")

with open('model_accuracy.json', 'w') as f:
    json.dump(accuracies, f, indent=2)
print(f"\n💾 Accuracies saved to model_accuracy.json")

# Save confusion matrix for Decision Tree (for evaluation.py)
cm = confusion_matrix(y_test, dt_pred)
np.save('models/dt_confusion_matrix.npy', cm)

# Save feature importance
np.save('models/feature_importance.npy', importance)
joblib.dump(feat_imp, 'models/feature_importance_named.pkl')

print("\n" + "=" * 60)
print("✅ ALL MODELS TRAINED SUCCESSFULLY!")
print("=" * 60)
print(f"\nModels saved in: models/")
print(f"Files:")
for f_name in os.listdir('models'):
    size = os.path.getsize(f'models/{f_name}')
    print(f"   📁 {f_name} ({size:,} bytes)")
