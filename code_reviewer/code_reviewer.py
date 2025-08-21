# code_reviewer.py

import os
import ast
from radon.complexity import cc_visit
from radon.metrics import mi_visit
import lizard
import textdistance
import hashlib


def analyze_python_file(filepath):
    """Returns basic code metrics for a given Python file."""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        src = f.read()

    try:
        tree = ast.parse(src)
    except SyntaxError:
        return {"error": "Could not parse file due to syntax error."}

    # Extract functions and classes
    funcs = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    # Cyclomatic complexity
    cc_results = cc_visit(src)
    cc_map = {b.name: b.complexity for b in cc_results}

    # Maintainability Index
    try:
        mi = mi_visit(src, True)
    except:
        mi = -1

    # Lizard metrics
    liz = lizard.analyze_file(filepath)
    avg_cc = liz.average_cyclomatic_complexity
    halstead = {
        "volume": getattr(liz, "halstead_volume", None),
        "difficulty": getattr(liz, "halstead_difficulty", None),
    }

    return {
        "functions": [f.name for f in funcs],
        "classes": [c.name for c in classes],
        "cyclomatic_complexity": cc_map,
        "maintainability_index": round(mi, 2),
        "avg_cyclomatic_complexity": round(avg_cc, 2),
        "halstead": halstead
    }

def fingerprint_file(filepath):
    """Returns a fingerprint of the AST for similarity detection."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        source = f.read()

    tree = ast.parse(source)
    dump = ast.dump(tree, annotate_fields=False)
    norm = "".join(dump.split())
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()

def compare_similarity(fp1, fp2):
    """Returns Jaccard similarity between two code fingerprints."""
    return round(textdistance.jaccard(fp1, fp2), 2)
