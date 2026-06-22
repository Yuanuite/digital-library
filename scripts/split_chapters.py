#!/usr/bin/env python3
"""Phase 4: Split full.md into chapters by week boundaries, fix heading levels."""
import re, os, shutil

PROJECT = os.path.expanduser("~/Documents/digital-library")
INPUT = f"{PROJECT}/out/ml-notes-v5/full.md"
IMAGES_SRC = f"{PROJECT}/out/ml-notes-v5/images"
OUTDIR = f"{PROJECT}/docs/books/ml/stanford-ml-notes"

os.makedirs(OUTDIR, exist_ok=True)
os.makedirs(f"{OUTDIR}/images", exist_ok=True)

with open(INPUT) as f:
    lines = f.readlines()

# Find week boundaries: lines starting with "## 第 N 周" or "## 附件"
week_starts = []
for i, line in enumerate(lines):
    if re.match(r'^## 第 \d+ 周\s*$', line.strip()):
        week_starts.append((i, line.strip()))
    elif line.strip() == '## 附件':
        week_starts.append((i, line.strip()))

print(f"Found {len(week_starts)} boundaries: {[w[1] for w in week_starts]}")

# Preamble is everything before the first "## 第 N 周"
preamble_end = week_starts[0][0] if week_starts else 0

# Write index.md from preamble
index_lines = lines[:preamble_end]
# Clean up the preamble for index.md: keep title, course overview, toc
with open(f"{OUTDIR}/index.md", 'w') as f:
    f.writelines(index_lines)
print(f"index.md: {len(index_lines)} lines (preamble)")

# Write chapter files
chapter_nums = []
for idx, (start, title) in enumerate(week_starts):
    end = week_starts[idx + 1][0] if idx + 1 < len(week_starts) else len(lines)

    if '附件' in title:
        chap_name = 'appendix'
        chap_title = '附件'
    else:
        week_match = re.search(r'第 (\d+) 周', title)
        week_num = int(week_match.group(1)) if week_match else idx + 1
        chap_name = f'ch{week_num:02d}'
        chap_title = title.replace('## ', '')

    chapter_lines = lines[start:end]

    # Fix heading levels in this chapter
    fixed_lines = []
    for line in chapter_lines:
        stripped = line.strip()
        if stripped.startswith('## '):
            # "## 第 N 周" → "# 第 N 周" (chapter title)
            if re.match(r'^## 第 \d+ 周', stripped):
                line = line.replace('## ', '# ', 1)
            # "## N、Name" or "## N. Name" → "## N、Name" (section, keep H2)
            elif re.match(r'^## \d+[、,.]', stripped):
                pass  # keep as ##
            # "## N.M Name" → "### N.M Name" (topic → H3)
            elif re.match(r'^## \d+\.\d+', stripped):
                line = line.replace('## ', '### ', 1)
            # "## 附件" or other top-level → "# ..."
            elif stripped in ('## 附件',):
                line = line.replace('## ', '# ', 1)
            # "## CS229" → "# CS229"
            elif stripped.startswith('## CS229'):
                line = line.replace('## ', '## ', 1)  # keep as H2 under appendix
            # "## 机器学习的数学基础" → "## ..."
            else:
                pass  # keep unknown patterns as-is

        fixed_lines.append(line)

    with open(f"{OUTDIR}/{chap_name}.md", 'w') as f:
        f.writelines(fixed_lines)

    print(f"{chap_name}.md: {len(fixed_lines)} lines ({chap_title})")
    chapter_nums.append(chap_name)

# Copy images if any exist
if os.path.isdir(IMAGES_SRC):
    for fname in os.listdir(IMAGES_SRC):
        src = os.path.join(IMAGES_SRC, fname)
        dst = os.path.join(OUTDIR, 'images', fname)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
    print(f"Copied {len(os.listdir(IMAGES_SRC))} images")

# Fix code-block comment-to-heading issue: inside ``` blocks,
# lines starting with "# " should be demoted to "## "
for ch_name in os.listdir(OUTDIR):
    if not ch_name.endswith('.md'):
        continue
    fpath = os.path.join(OUTDIR, ch_name)
    with open(fpath) as f:
        content = f.read()

    in_code = False
    fixed = []
    for line in content.split('\n'):
        if line.strip().startswith('```'):
            in_code = not in_code
            fixed.append(line)
        elif in_code and line.startswith('# ') and not line.startswith('## '):
            fixed.append('##' + line[1:])  # demote # → ## inside code blocks
        else:
            fixed.append(line)

    with open(fpath, 'w') as f:
        f.write('\n'.join(fixed))

print("\nDone! Chapter files written to:", OUTDIR)
