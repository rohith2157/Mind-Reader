import json
import os

with open('models/game.ipynb', 'r', encoding='utf-8') as f:
    d = json.load(f)

for c in d['cells']:
    if c['cell_type'] == 'code':
        source = c['source']
        for j, line in enumerate(source):
            if 'df = pd.read_csv(' in line:
                source[j] = """import os
data_path = 'mindreader_data.csv'
if not os.path.exists(data_path):
    data_path = '../mindreader_data.csv'
df = pd.read_csv(data_path)
"""
            if 'os.makedirs(' in line and 'data' in line and 'mindreader_data' not in line:
                source[j] = """data_dir = 'data' if os.path.exists('mindreader_data.csv') else '../data'
os.makedirs(data_dir, exist_ok=True)
"""
            if 'train_data.to_csv(' in line:
                source[j] = "train_data.to_csv(f'{data_dir}/train_data.csv', index=False)\n"
            if 'test_data.to_csv(' in line:
                source[j] = "test_data.to_csv(f'{data_dir}/test_data.csv', index=False)\n"
            if 'Saved: data/train' in line:
                source[j] = "print(f'\\nSaved: {data_dir}/train_data.csv ({len(train_data)} rows)')\n"
            if 'Saved: data/test' in line:
                source[j] = "print(f'Saved: {data_dir}/test_data.csv ({len(test_data)} rows)')\n"

            # Fix accuracy save path
            if 'with open(' in line and 'model_accuracy.json' in line:
                source[j] = """acc_path = 'model_accuracy.json' if os.path.exists('mindreader_data.csv') else '../model_accuracy.json'
with open(acc_path, 'w') as f:
"""
        c['source'] = source

with open('models/game.ipynb', 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=1)
