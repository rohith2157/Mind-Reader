import json

with open('models/game.ipynb', 'r', encoding='utf-8') as f:
    d = json.load(f)

source = d['cells'][35]['source']
new_source = []
for line in source:
    if line.startswith("        files.download('model_accuracy.json')"):
        new_source.append("    files.download('model_accuracy.json')\n")
    else:
        new_source.append(line)
        
d['cells'][35]['source'] = new_source

with open('models/game.ipynb', 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=1)
