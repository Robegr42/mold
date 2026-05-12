import json
import os

results_dir = 'results/'
data = []

for filename in os.listdir(results_dir):
    if filename.endswith('.json'):
        with open(os.path.join(results_dir, filename), 'r') as f:
            try:
                res = json.load(f)
                model = res.get('config', {}).get('model', 'unknown')
                pipeline = res.get('config', {}).get('pipeline', 'unknown')
                metrics = res.get('metrics', {})
                f1 = metrics.get('f1', 0)
                precision = metrics.get('precision', 0)
                recall = metrics.get('recall', 0)
                
                # Check for ni (no invariants) in filename if not in pipeline name
                is_ni = 'ni' in filename or pipeline.endswith('-ni')
                
                data.append({
                    'file': filename,
                    'model': model,
                    'pipeline': pipeline,
                    'f1': f1,
                    'precision': precision,
                    'recall': recall,
                    'is_ni': is_ni
                })
            except:
                pass

# Sort by F1 descending
data.sort(key=lambda x: x['f1'], reverse=True)

print("File | Model | Pipeline | F1 | P | R | NI")
print("--- | --- | --- | --- | --- | --- | ---")
for d in data:
    print(f"{d['file']} | {d['model']} | {d['pipeline']} | {d['f1']:.4f} | {d['precision']:.4f} | {d['recall']:.4f} | {d['is_ni']}")
