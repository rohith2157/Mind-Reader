import json

with open('models/game.ipynb', 'r', encoding='utf-8') as f:
    d = json.load(f)

for c in d['cells']:
    if c['cell_type'] == 'code':
        source = c['source']
        for i, line in enumerate(source):
            if "df = pd.read_csv(" in line:
                source[i] = "data_path = 'mindreader_data.csv' if os.path.exists('mindreader_data.csv') else '../mindreader_data.csv'\n"
                source.insert(i+1, "df = pd.read_csv(data_path)\n")
                break
        
        # Clean up old redundant lines setting data_path
        new_source = []
        skip_next = False
        for line in source:
            if skip_next:
                skip_next = False
                continue
            if line == "data_path = 'mindreader_data.csv'\n" or line.startswith("if not os.path.exists("):
                skip_next = True if line.startswith("if not os.path.exists(") else False
                continue
            if line == "    data_path = '../mindreader_data.csv'\n":
                continue
            
            # Prevent double inserting the df = pd.read_csv
            if line == "df = pd.read_csv(data_path)\n" and "df = pd.read_csv(data_path)\n" in new_source:
                continue
                
            new_source.append(line)
        c['source'] = new_source

with open('models/game.ipynb', 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=1)
