import importlib, traceback, sys, re, os

# Ensure project root is on sys.path so top-level package imports like `apps` work
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    importlib.import_module('apps.codexgraph_agent.help')
    print('IMPORT_OK')
except Exception:
    tb = traceback.format_exc()
    print(tb)
    m = re.search(r"No module named '([^']+)'", tb)
    if m:
        print('MISSING_MODULE:'+m.group(1))
    sys.exit(1)
