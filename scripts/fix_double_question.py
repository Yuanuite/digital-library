#!/usr/bin/env python3
"""Phase 2: Broader ?? OCR fix — context-based replacement for ML course notes."""
import re, os

OUTDIR = os.path.expanduser("~/Documents/digital-library/docs/books/ml/stanford-ml-notes")

# Broad replacement rules ordered from most specific to most general
RULES = [
    # === Cost function J ===
    (r'代价函数\?\?', '代价函数J'),
    (r'函数\?\?\(', '函数J('),
    (r'使\?\?\(', '使J('),
    (r'最小化任何代价函数\?\?', '最小化任何代价函数J'),

    # === Learning rate α ===
    (r'\?\?是学习率', 'α是学习率'),
    (r'学习速率\?\?', '学习速率α'),
    (r'减小\?\?(?![一-鿿]{2})', '减小α'),  # only if not followed by two CJK chars
    (r'\?\?太小', 'α太小'),
    (r'\?\?太大', 'α太大'),
    (r'\?\?保持不变', 'α保持不变'),

    # === m (number of examples) ===
    (r'用\?\?来表示训练样本', '用m来表示训练样本'),
    (r'\?\?代表了训练样本', 'm代表了训练样本'),
    (r'\?\?代表训练集中实例', 'm代表训练集中实例'),
    (r'设\?\?个训练', '设m个训练'),
    (r'\?\?个训练', 'm个训练'),

    # === Dimension context: m rows, n cols ===
    (r'\?\?行和\?\?列', 'm行和n列'),
    (r'\?\?行([，,])', r'm行\1'),
    (r'\?\?列', 'n列'),
    (r'具有\?\?个元素', '具有n个元素'),
    (r'\?\?个元素的向量', 'n个元素的向量'),
    (r'\?\?维向量', 'n维向量'),

    # === Index i, j ===
    (r'第\?\?个观察实例', '第i个观察实例'),
    (r'第\?\?个元素', '第i个元素'),
    (r'第\?\?行', '第i行'),
    (r'第\?\?列', '第j列'),
    (r'第\?\?个\?\?', lambda m: m.group().replace('??', 'i', 1).replace('??', 'i')),

    # === x / y (input/output) ===
    (r'\?\?代表特征的数量', 'n代表特征的数量'),  # must be before broader rule
    (r'\?\?代表特征', 'x代表特征'),
    (r'\?\?代表目标', 'y代表目标'),
    (r'\?\?轴', 'y轴'),
    (r'\?\?值[，。]', 'x值。'),  # too aggressive, skip

    # === Matrix A / B ===
    (r'矩阵\?\?的', '矩阵A的'),
    (r'表示\?\?为', '表示A为'),
    (r'\?\?的第\?\?', lambda m: m.group().replace('??', 'A', 1)),  # "A的第j列"
    (r'表示矩阵\?\?', '表示矩阵A'),

    # === Vectors ===
    (r'向量\?\?将', '向量x将'),
    (r'向量\?\?的', '向量x的'),

    # === In LaTeX context: fix broken $...??...$  ===
    # "??(??)" in text → "J(θ)" — common cost function pattern
    (r'([^$])\?\?\(\?\?\)', r'\1J(θ)'),

    # === Common multi-character patterns ===
    (r'\?\?\(\?\?\)', 'J(θ)'),  # most common: cost function with theta
    (r'和\?\? ?= ?([0-9])', r'和j=\1'),  # "和j=0"
    (r'当\?\?=', '当j='),

    # === n (number of features / dimension) ===
    (r'\?\?\+1个参数', 'n+1个参数'),
    (r'\?\?\+1维', 'n+1维'),
    (r'\?\?个变量', 'n个变量'),
    (r'\?\?个特征', 'n个特征'),

    # === Training instance index i ===
    (r'第\?\?个训练实例', '第i个训练实例'),
    (r'第\?\?个特征', '第j个特征'),

    # === Transpose superscript T ===
    (r'上标\?\?代表', '上标T代表'),

    # === Learning rate α (more patterns) ===
    (r'学习率\?\?过小', '学习率α过小'),
    (r'学习率\?\?过大', '学习率α过大'),
    (r'\?\? ?= ?([0-9]+\.[0-9]+)', r'α = \1'),  # "?? = 0.01" → "α = 0.01"

    # === X (feature matrix) and y (target vector) ===
    (r'特征矩阵[为是]\?\?', '特征矩阵为 X'),
    (r'向量\?\?，', '向量 y，'),
    (r'参数\?\?的替代', '参数θ的替代'),

    # === Matrix multiplication context ===
    (r'矩阵\?\?\'', "矩阵X'"),  # X'X pattern
    (r'\?\?中的列数', 'A中的列数'),
    (r'\?\?中的行数', 'B中的行数'),
    (r'表达\?\?[,。]', '表达A。'),

    # === More appendix patterns ===
    (r'按行写\?\?', '按行写A'),
    (r'按列写\?\?', '按列写A'),
    (r'把\?\?用列表示', '把A用列表示'),
    (r'等于\?\?和\?\?的', '等于x和A的'),

    # === Very broad patterns — apply last ===
    (r'小写的\?\?', '小写的m'),
    (r'\?\?\(\?\?\)', 'J(θ)'),
    (r'\(\?\?,\?\?\)', '(x,y)'),
    (r'从\?\?到\?\?', '从x到y'),
]

def fix_file(path):
    with open(path) as f:
        text = f.read()

    count_before = text.count('??')
    original = text

    for pattern, replacement in RULES:
        if callable(replacement):
            text = re.sub(pattern, replacement, text)
        else:
            text = re.sub(pattern, replacement, text)

    # Additional aggressive fix: in Chinese text blocks (not in LaTeX $$),
    # remaining "??" followed by Chinese punctuation or newline
    # Try context-free replacements for remaining ?? in body text
    lines = text.split('\n')
    fixed_lines = []
    in_code = False
    for line in lines:
        if line.strip().startswith('```'):
            in_code = not in_code
            fixed_lines.append(line)
            continue
        if in_code:
            fixed_lines.append(line)
            continue

        # Skip lines that are pure LaTeX
        stripped = line.strip()
        if stripped.startswith('$$') or stripped.startswith('$') and not any(c in stripped[1:] for c in '??'):
            fixed_lines.append(line)
            continue

        # In mixed Chinese-text lines, remaining ?? are often:
        # "??(??)" → "J(θ)"
        line = re.sub(r'\?\?\(\?\?\)', 'J(θ)', line)
        # "??₁" "??₀" → "θ₁" "θ₀"
        line = re.sub(r'\?\?([₀₁₂₃₄₅₆₇₈₉])', r'θ\1', line)
        # "m×??" → "m×n" (matrix dimensions)
        line = re.sub(r'×\?\?([，。,、\s])', r'×n\1', line)
        # "??×??" → "m×n"
        line = re.sub(r'\?\?×\?\?', 'm×n', line)

        fixed_lines.append(line)

    text = '\n'.join(fixed_lines)

    count_after = text.count('??')
    removed = count_before - count_after

    if removed > 0:
        with open(path, 'w') as f:
            f.write(text)

    return count_before, count_after

total_before = total_after = 0
for fname in sorted(os.listdir(OUTDIR)):
    if fname.endswith('.md'):
        fpath = os.path.join(OUTDIR, fname)
        before, after = fix_file(fpath)
        total_before += before
        total_after += after
        if before != after:
            print(f"  {fname}: {before} → {after} ({before-after} fixed)")

print(f"\nTotal: {total_before} → {total_after} ({total_before-total_after} fixed, {total_after} remaining)")
