"""Dataset quality analysis script for QA validation."""
import csv
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[3] / "backend" / "data"

# Check eval_set.csv
with open(DATA_DIR / "eval_set.csv", newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

print(f'Total rows: {len(rows)}')
labels = [int(r['label']) for r in rows]
print(f'Label distribution: scam={sum(labels)}, legit={len(labels)-sum(labels)}')
languages = {}
for r in rows:
    l = r['language']
    languages[l] = languages.get(l, 0) + 1
print('Language distribution:', json.dumps(languages))
categories = {}
for r in rows:
    c = r['category']
    categories[c] = categories.get(c, 0) + 1
print('Category distribution:', json.dumps(categories))
sources = set(r['source'] for r in rows)
print('Sources:', sources)
ids = [r['id'] for r in rows]
dup_ids = [i for i in ids if ids.count(i) > 1]
print('Duplicate IDs:', dup_ids if dup_ids else 'None - all unique')

# Check dev_set and heldout_set
with open(DATA_DIR / "dev_set.csv", newline='', encoding='utf-8') as f:
    dev = list(csv.DictReader(f))
with open(DATA_DIR / "heldout_set.csv", newline='', encoding='utf-8') as f:
    heldout = list(csv.DictReader(f))
print(f'dev_set rows: {len(dev)}, heldout_set rows: {len(heldout)}')

# Train/test contamination check: are eval IDs in dev/heldout?
eval_ids = set(r['id'] for r in rows)
dev_ids = set(r['id'] for r in dev)
heldout_ids = set(r['id'] for r in heldout)
print(f'Eval-dev overlap: {eval_ids & dev_ids}')
print(f'Eval-heldout overlap: {eval_ids & heldout_ids}')
