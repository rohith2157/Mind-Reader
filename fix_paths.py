import json

with open('models/game.ipynb', 'r', encoding='utf-8') as f:
    d = json.load(f)

for c in d['cells']:
    if c['cell_type'] == 'code':
        source = "".join(c['source'])
        
        # Original dataset path -> relative to parent directory
        source = source.replace("pd.read_csv('mindreader_data.csv')", "pd.read_csv('../mindreader_data.csv')")
        
        # Original train/test paths -> relative to parent directory
        source = source.replace("os.makedirs('data'", "os.makedirs('../data'")
        source = source.replace("'data/train_data.csv'", "'../data/train_data.csv'")
        source = source.replace("'data/test_data.csv'", "'../data/test_data.csv'")
        
        # Accuracy file relative to parent directory
        source = source.replace("'model_accuracy.json'", "'../model_accuracy.json'")
        
        c['source'] = source.splitlines(True)

with open('models/game.ipynb', 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=1)
