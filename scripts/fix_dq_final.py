#!/usr/bin/env python3
"""Final pass: fix remaining ?? with space-tolerant patterns."""
import re, os

OUTDIR = os.path.expanduser("~/Documents/digital-library/docs/books/ml/stanford-ml-notes")

# Final aggressive rules with optional whitespace
FINAL_RULES = [
    # m (training examples)
    (r'用小写的\?\?', '用小写的m'),
    (r'\?\? *代表训练集中实例', 'm 代表训练集中实例'),
    (r'\?\? *个训练', 'm个训练'),

    # x, y
    (r'\?\? *代表特征', 'x 代表特征'),
    (r'\?\? *代表目标', 'y 代表目标'),
    (r'\(\?\? *, *\?\?\)', '(x, y)'),  # (x,y)

    # i (index)
    (r'第 *\?\? *个观察', '第 i 个观察'),
    (r'第 *\?\? *个训练', '第 i 个训练'),
    (r'第 *\?\? *行', '第 i 行'),
    (r'第 *\?\? *列', '第 j 列'),
    (r'第 *\?\? *个特征', '第 j 个特征'),
    (r'第 *\?\? *个元素', '第 i 个元素'),

    # Greek letters
    (r'学习率 *\?\?', '学习率 α'),
    (r'\?\? *是学习率', 'α 是学习率'),

    # J (cost function) — broad patterns
    (r'代价函数 *\?\?', '代价函数 J'),
    (r'函数 *\?\? *\(', '函数 J ('),

    # n (dimension)
    (r'\?\? *代表特征的数量', 'n 代表特征的数量'),
    (r'\?\? *个变量', 'n个变量'),
    (r'\?\?\+ *1', 'n+1'),

    # Matrix A
    (r'矩阵 *\?\? *的', '矩阵 A 的'),
    (r'表示 *\?\? *为', '表示 A 为'),

    # Common formulas
    (r'\?\? *\( *\?\? *\)', 'J(θ)'),
    (r'从 *\?\? *到 *\?\?', '从 x 到 y'),

    # x/y axis and input/output
    (r'\?\? *轴', 'y轴'),
    (r'输入.*?\?\? *值', lambda m: m.group().replace('??', 'x')),
    (r'输出.*?\?\? *值', lambda m: m.group().replace('??', 'y')),
    (r'\?\? *代表输入', 'x 代表输入'),
    (r'\?\? *代表输出', 'y 代表输出'),

    # Superscript T (transpose)
    (r'上标 *\?\?', '上标 T'),
]

# Multi-pass: keep applying until no more changes
for fname in sorted(os.listdir(OUTDIR)):
    if not fname.endswith('.md'):
        continue
    fpath = os.path.join(OUTDIR, fname)
    with open(fpath) as f:
        text = f.read()

    count_before = text.count('??')
    if count_before == 0:
        continue

    # Apply rules in multiple passes
    for _ in range(3):  # up to 3 passes
        for pattern, replacement in FINAL_RULES:
            if callable(replacement):
                text = re.sub(pattern, replacement, text)
            else:
                text = re.sub(pattern, replacement, text)

    # Also: in lines with Chinese chars, replace remaining "??" after specific words
    lines = text.split('\n')
    fixed_lines = []
    for line in lines:
        if line.strip().startswith('```') or line.strip().startswith('$$'):
            fixed_lines.append(line)
            continue
        # Replace remaining "??" in known contexts
        # "??值" at end of sentence → "y值"
        line = re.sub(r'\?\?值', 'y值', line)
        fixed_lines.append(line)
    text = '\n'.join(fixed_lines)

    count_after = text.count('??')
    if count_after < count_before:
        with open(fpath, 'w') as f:
            f.write(text)
        print(f"  {fname}: {count_before} → {count_after} ({count_before-count_after} fixed)")

print("\nDone!")
