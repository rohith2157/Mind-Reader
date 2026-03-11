import json

with open('models/game.ipynb', 'r', encoding='utf-8') as f:
    d = json.load(f)

# Cell 7
cell7 = d['cells'][7]['source']
new_cell7 = []
for line in cell7:
    if line.startswith('from google.colab import files'):
        new_cell7.extend([
            'try:\n',
            '    from google.colab import files\n',
            '    uploaded = files.upload()\n',
            'except ImportError:\n',
            '    print("Not running in Google Colab. Using local file.")\n'
        ])
    elif line.startswith('uploaded = files.upload()'):
        pass
    else:
        new_cell7.append(line)
d['cells'][7]['source'] = new_cell7

# Cell 35
cell35 = d['cells'][35]['source']
new_cell35 = []
for line in cell35:
    if line.startswith('from google.colab import files'):
        new_cell35.extend([
            'try:\n',
            '    from google.colab import files\n'
        ])
    elif line.startswith('for fname in os.listdir'):
        new_cell35.append('    ' + line)
    elif line.startswith('    files.download'):
        new_cell35.append('    ' + line)
    elif line.startswith('    print(f"  Downloaded: {fname}")'):
        new_cell35.append('    ' + line)
    elif line.startswith('files.download('):
        new_cell35.append('    ' + line)
    elif line.startswith('print("  Downloaded: model_accuracy'):
        new_cell35.append('    ' + line)
        new_cell35.extend([
            'except ImportError:\n',
            '    print("Not running in Google Colab. Files are already saved locally.")\n'
        ])
    else:
        new_cell35.append(line)
d['cells'][35]['source'] = new_cell35

with open('models/game.ipynb', 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=1)
