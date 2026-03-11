# Step 1.1: Install required libraries
# !pip install pandas numpy scikit-learn joblib matplotlib seaborn -q
print("All libraries installed successfully!")

# --- CELL ---

# Step 1.2: Import all required libraries

import pandas as pd
import numpy as np
import os, json, warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

import joblib
import matplotlib.pyplot as plt
import seaborn as sns

print("All libraries imported successfully!")

# --- CELL ---

# Step 1.3: Upload and Load the dataset
try:
    from google.colab import files
    uploaded = files.upload()
except ImportError:
    print("Not running in Google Colab. Using local file.")

import os
data_path = 'mindreader_data.csv'
if not os.path.exists(data_path):
    data_path = '../mindreader_data.csv'
df = pd.read_csv(data_path)

print(f"Dataset loaded successfully!")
print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")
print(f"Unique entities: {df['name'].nunique()}")
print(f"\nCategory distribution:")
print(df['category'].value_counts())
print(f"\nFirst 10 rows of data:")
df.head(10)

# --- CELL ---

# Step 1.4: Explore data structure
print("Data types in our dataset:")
print(df.dtypes.value_counts())

print(f"\nColumn names:")
print(list(df.columns))

print(f"\nStatistical summary of numeric columns:")
df.describe()

# --- CELL ---

# Step 2.1: Check and handle missing values
print("Missing values per column:")
missing = df.isnull().sum()
missing_cols = missing[missing > 0]

if len(missing_cols) > 0:
    print(missing_cols)
    print(f"\nTotal missing values: {missing.sum()}")
else:
    print("No missing values found! Data is clean.")

df = df.fillna(0)
print(f"\nAfter cleaning - Total missing: {df.isnull().sum().sum()}")

# --- CELL ---

# Step 2.2: Encode text labels into numbers using LabelEncoder
le_name = LabelEncoder()
df['name_encoded'] = le_name.fit_transform(df['name'])

le_category = LabelEncoder()
df['category_encoded'] = le_category.fit_transform(df['category'])

print(f"Name encoder: {len(le_name.classes_)} unique names encoded (0 to {len(le_name.classes_)-1})")
print(f"Category encoder: {list(le_category.classes_)}")
print(f"\nSample encoding (text -> number):")
print(df[['name', 'name_encoded', 'category', 'category_encoded']].drop_duplicates().head(10))

# --- CELL ---

# Step 2.3: Prepare feature matrix (X) and target vector (y)
feature_cols = [col for col in df.columns
                if col not in ['name', 'category', 'name_encoded', 'category_encoded']]

X = df[feature_cols].values
y = df['name_encoded'].values

print(f"Number of features: {len(feature_cols)}")
print(f"\nAll {len(feature_cols)} feature columns:")
for i, col in enumerate(feature_cols, 1):
    print(f"  {i:2d}. {col}")
print(f"\nX (features) shape: {X.shape}  - {X.shape[0]} samples, {X.shape[1]} features each")
print(f"y (target) shape:   {y.shape}  - {y.shape[0]} labels to predict")

# --- CELL ---

# Step 3.1: Split data into 70% training and 30% testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Training samples: {X_train.shape[0]} ({X_train.shape[0]/len(X)*100:.0f}%)")
print(f"Testing samples:  {X_test.shape[0]} ({X_test.shape[0]/len(X)*100:.0f}%)")

# Save train and test data as CSV files
data_dir = 'data' if os.path.exists('mindreader_data.csv') else '../data'
os.makedirs(data_dir, exist_ok=True)

train_data, test_data = train_test_split(df, test_size=0.2, random_state=42)
train_data.to_csv(f'{data_dir}/train_data.csv', index=False)
test_data.to_csv(f'{data_dir}/test_data.csv', index=False)

print(f'\nSaved: {data_dir}/train_data.csv ({len(train_data)} rows)')
print(f'Saved: {data_dir}/test_data.csv ({len(test_data)} rows)')


# --- CELL ---

# Step 4.1: Train Decision Tree using ID3 algorithm (entropy = information gain)
dt_model = DecisionTreeClassifier(
    criterion='entropy',
    max_depth=20,
    min_samples_split=2,
    random_state=42
)

dt_model.fit(X_train, y_train)

print("Decision Tree (ID3) trained successfully!")
print(f"Actual tree depth: {dt_model.get_depth()}")
print(f"Number of leaf nodes: {dt_model.get_n_leaves()}")
print(f"Number of features used: {dt_model.n_features_in_}")

# --- CELL ---

# Step 4.2: Test the model on unseen test data
y_pred = dt_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"Decision Tree (ID3) Test Accuracy: {accuracy * 100:.2f}%")
print(f"Correct predictions: {int(accuracy * len(y_test))} out of {len(y_test)}")

# --- CELL ---

# Step 4.3: Save the trained model and encoders to modelcolab/ folder
os.makedirs('modelcolab', exist_ok=True)

joblib.dump(dt_model, 'modelcolab/dt_model.pkl')
joblib.dump(le_name, 'modelcolab/label_encoder_name.pkl')
joblib.dump(le_category, 'modelcolab/label_encoder_category.pkl')
joblib.dump(feature_cols, 'modelcolab/feature_cols.pkl')

acc_dict = {'Decision Tree (ID3)': round(accuracy * 100, 2)}
acc_path = 'model_accuracy.json' if os.path.exists('mindreader_data.csv') else '../model_accuracy.json'
with open(acc_path, 'w') as f:
    json.dump(acc_dict, f, indent=2)

print("All files saved to modelcolab/:")
for f_name in os.listdir('modelcolab'):
    size = os.path.getsize(f'modelcolab/{f_name}')
    print(f"  {f_name} ({size:,} bytes)")
print(f"\nAccuracy saved to model_accuracy.json")
print(f"\n>> Download the modelcolab/ folder and place it in models/modelcolab/ in the project <<")

# --- CELL ---

# Step 5.1: Classification Report
print("=" * 60)
print("  CLASSIFICATION REPORT")
print("=" * 60)
print(classification_report(y_test, y_pred, zero_division=0))

# --- CELL ---

# Step 5.2: Confusion Matrix Heatmap (category-level)
y_cat = le_category.transform(df['category'])
_, X_test_cat, _, y_test_cat = train_test_split(X, y_cat, test_size=0.2, random_state=42)

dt_cat = DecisionTreeClassifier(criterion='entropy', max_depth=10, random_state=42)
y_cat_train = le_category.transform(train_data['category'])
dt_cat.fit(X_train, y_cat_train)
y_cat_pred = dt_cat.predict(X_test_cat)

cm = confusion_matrix(y_test_cat, y_cat_pred)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=le_category.classes_,
            yticklabels=le_category.classes_)
plt.xlabel('Predicted Category')
plt.ylabel('Actual Category')
plt.title('Confusion Matrix - Decision Tree (Category Level)')
plt.tight_layout()
plt.show()

cat_acc = accuracy_score(y_test_cat, y_cat_pred)
print(f"Category-level accuracy: {cat_acc*100:.2f}%")

# --- CELL ---

# Step 5.3: Feature Importance - Top 15 most important features
importance = dt_model.feature_importances_
feat_imp = sorted(zip(feature_cols, importance), key=lambda x: x[1], reverse=True)

top_n = 15
features = [f[0] for f in feat_imp[:top_n]]
scores = [f[1] for f in feat_imp[:top_n]]

plt.figure(figsize=(10, 6))
plt.barh(features[::-1], scores[::-1], color='teal')
plt.xlabel('Importance Score (Information Gain)')
plt.title(f'Top {top_n} Feature Importance - Decision Tree (ID3)')
plt.tight_layout()
plt.show()

print("\nAll features ranked by importance:")
for i, (feat, imp) in enumerate(feat_imp, 1):
    bar = "*" * int(imp * 50)
    print(f"  {i:2d}. {feat:25s} {imp:.4f}  {bar}")

# --- CELL ---

# Step 5.4: Final Summary + Download model files
print("=" * 55)
print("   AI MIND READER - TRAINING SUMMARY")
print("=" * 55)
print(f"   Model:          Decision Tree (ID3)")
print(f"   Criterion:      Entropy (Information Gain)")
print(f"   Dataset:        {df.shape[0]} rows, {len(feature_cols)} features")
print(f"   Unique entities:{df['name'].nunique()}")
print(f"   Train set:      {X_train.shape[0]} samples (70%)")
print(f"   Test set:       {X_test.shape[0]} samples (30%)")
print(f"   Accuracy:       {accuracy * 100:.2f}%")
print(f"   Tree depth:     {dt_model.get_depth()}")
print(f"   Leaf nodes:     {dt_model.get_n_leaves()}")
print(f"   Top feature:    {feat_imp[0][0]}")
print(f"   Model saved:    modelcolab/dt_model.pkl")
print("=" * 55)

# Download model files from Colab to local machine
print("\nDownloading model files...")
try:
    from google.colab import files
    for fname in os.listdir('modelcolab'):
        files.download(f'modelcolab/{fname}')
        print(f"  Downloaded: {fname}")

        files.download('model_accuracy.json')
    print("  Downloaded: model_accuracy.json")
except ImportError:
    print("Not running in Google Colab. Files are already saved locally.")

print("\n>> Place these files in: mindreader_project/models/modelcolab/ <<")
print(">> Then run: python app.py - to start the web game! <<")