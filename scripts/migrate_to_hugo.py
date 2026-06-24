#!/usr/bin/env python3
"""Migrate docs/ to content/ for Hugo architecture."""
import os, re, shutil

BASE = "/Users/qingyuan/Documents/digital-library"
DOCS = f"{BASE}/docs"
CONTENT = f"{BASE}/content"

if os.path.exists(CONTENT):
    shutil.rmtree(CONTENT)
os.makedirs(CONTENT)

# Section index pages
for section in ['books', 'papers', 'notes']:
    dst_dir = f"{CONTENT}/{section}"
    os.makedirs(dst_dir, exist_ok=True)
    src = f"{DOCS}/{section}/index.md"
    if os.path.exists(src):
        shutil.copy(src, f"{dst_dir}/_index.md")
        print(f"  {section}/index.md → {section}/_index.md")

# About page
shutil.copy(f"{DOCS}/about.md", f"{CONTENT}/about.md")
print("  about.md")

# Reference (element templates from yuulibrary)
os.makedirs(f"{CONTENT}/reference", exist_ok=True)
ref_src = "/tmp/yuulibrary/content/reference/elements.md"
if os.path.exists(ref_src):
    shutil.copy(ref_src, f"{CONTENT}/reference/elements.md")
    with open(f"{CONTENT}/reference/_index.md", 'w') as f:
        f.write('---\ntitle: "元素模板"\nweight: 1\n---\n\n# 元素模板速查\n')
    print("  reference/")

# Flatten books: docs/books/<category>/<slug> → content/books/<slug>
for cat in os.listdir(f"{DOCS}/books"):
    cat_path = f"{DOCS}/books/{cat}"
    if not os.path.isdir(cat_path):
        continue
    for slug in os.listdir(cat_path):
        src = f"{cat_path}/{slug}"
        dst = f"{CONTENT}/books/{slug}"
        if os.path.isdir(src):
            shutil.copytree(src, dst)
            idx_src = f"{dst}/index.md"
            idx_dst = f"{dst}/_index.md"
            if os.path.exists(idx_src):
                os.rename(idx_src, idx_dst)
            print(f"  books/{cat}/{slug} → books/{slug}")

# Migrate papers
for field in os.listdir(f"{DOCS}/papers"):
    src = f"{DOCS}/papers/{field}"
    dst = f"{CONTENT}/papers/{field}"
    if os.path.isdir(src) and not field.startswith('.'):
        shutil.copytree(src, dst)
        for root, dirs, files in os.walk(dst):
            if 'index.md' in files and root != dst:
                os.rename(f"{root}/index.md", f"{root}/_index.md")
        print(f"  papers/{field}")

# Migrate notes
for item in os.listdir(f"{DOCS}/notes"):
    src = f"{DOCS}/notes/{item}"
    dst = f"{CONTENT}/notes/{item}"
    if os.path.isfile(src) and item.endswith('.md'):
        shutil.copy(src, dst)
        print(f"  notes/{item}")

# Convert shortcodes in all content
def convert_shortcodes(text):
    # <p class="caption">content</p> → {{< caption >}}content{{< /caption >}}
    text = re.sub(r'<p class="caption"[^>]*>\s*(.*?)\s*</p>', r'{{< caption >}}\1{{< /caption >}}', text, flags=re.DOTALL)

    # <div class="solution" markdown="1"> ... </div> → {{< solution >}} ... {{< /solution >}}
    # Match paired solution divs
    def replace_solution(m):
        inner = m.group(1)
        return '{{< solution >}}' + inner + '{{< /solution >}}'
    text = re.sub(r'<div class="solution"[^>]*>(.*?)</div>', replace_solution, text, flags=re.DOTALL)

    # Remove standalone <div align="center" markdown> (opening only, keep content)
    text = re.sub(r'<div align="center" markdown>\s*', '', text)

    return text

for root, dirs, files in os.walk(CONTENT):
    for fname in files:
        if fname.endswith('.md'):
            path = os.path.join(root, fname)
            with open(path) as f:
                orig = f.read()
            new = convert_shortcodes(orig)
            if new != orig:
                with open(path, 'w') as f:
                    f.write(new)
                print(f"  converted: {os.path.relpath(path, CONTENT)}")

print("\nDone!")
