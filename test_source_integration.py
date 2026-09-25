import ast
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def exports(path):
    tree=ast.parse(path.read_text(encoding="utf-8"))
    return {n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))}

def db_imports(path):
    tree=ast.parse(path.read_text(encoding="utf-8"))
    result=set()
    for n in ast.walk(tree):
        if isinstance(n,ast.ImportFrom) and n.module=="db":
            result.update(a.name for a in n.names)
    return result

db_names=exports(ROOT/"db.py")
for rel in ("tools/product_tools.py","services/article_service.py"):
    missing=db_imports(ROOT/rel)-db_names
    assert not missing, f"{rel}: missing db exports {sorted(missing)}"

for rel in ("harness/runner.py","test_harness.py","sql/.gitkeep"):
    assert (ROOT/rel).exists(), rel

d=(ROOT/"Dockerfile").read_text(encoding="utf-8")
for line in ("COPY test_harness.py ./","COPY harness/ ./harness/","COPY sql/ ./sql/"):
    assert line in d, line
print("Source integration checks passed.")
