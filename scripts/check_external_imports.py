"""
扫描指定目录下的 Python 文件，静态提取 import 语句，汇总外部顶级包名（排除本仓库内包如 apps, modelscope_agent），
然后在当前 Python 运行环境中尝试 import，每行输出结果：OK 或 MISSING: exception
"""
import ast
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_DIRS = [ROOT / 'apps' / 'codexgraph_agent', ROOT / 'modelscope_agent']

def collect_imports(path):
    names = set()
    try:
        tree = ast.parse(path.read_text(encoding='utf-8'))
    except Exception:
        return names
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                names.add(n.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module.split('.')[0])
    return names

all_imports = set()
for d in TARGET_DIRS:
    if not d.exists():
        continue
    for py in d.rglob('*.py'):
        all_imports.update(collect_imports(py))

# filter out local packages (those that are top-level package names in this repo)
local_packages = set()
for child in ROOT.iterdir():
    if child.is_dir() and (child / '__init__.py').exists():
        local_packages.add(child.name)
# also include apps and modelscope_agent as local
local_packages.update({'apps', 'modelscope_agent'})

external_imports = sorted(x for x in all_imports if x and x not in local_packages)

print('# External top-level imports found:')
for name in external_imports:
    print(name)

print('\n# Import test results:')
for name in external_imports:
    try:
        __import__(name)
        print(f'OK: {name}')
    except Exception as e:
        print(f'MISSING: {name}   -- {e.__class__.__name__}: {e}')

# Exit code 0
