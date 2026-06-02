import re
import os
pattern = re.compile(r'[\u4e00-\u9fff]+')
results = {}
for root, dirs, files in os.walk('.'):
    for fn in files:
        path = os.path.join(root, fn)
        if path.startswith('.\\build') or path.startswith('.\\.git'):
            continue
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    if pattern.search(line):
                        results.setdefault(path, []).append((i, line.rstrip('\n')))
        except Exception:
            pass
for path in sorted(results):
    print('FILE:', path)
    for i, line in results[path]:
        print(f'{i}: {line}')
    print()
