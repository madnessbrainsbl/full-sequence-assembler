#!/usr/bin/env python3
import os
import ast

class CmdVisitor(ast.NodeVisitor):
    def __init__(self, file_path):
        self.file_path = file_path
        self.entries = []

    def visit_Call(self, node):
        func = node.func
        if isinstance(func, ast.Attribute):
            name = func.attr
        elif isinstance(func, ast.Name):
            name = func.id
        else:
            name = None
        # Capture sendDiagCmd calls
        if name == 'sendDiagCmd':
            cmd = None
            if node.args:
                arg0 = node.args[0]
                if isinstance(arg0, ast.Str):
                    cmd = arg0.s
                else:
                    try:
                        cmd = ast.literal_eval(arg0)
                    except Exception:
                        cmd = None
            params = []
            for p in node.args[1:]:
                if isinstance(p, ast.Str):
                    params.append(p.s)
                elif isinstance(p, ast.Num):
                    params.append(p.n)
                else:
                    try:
                        params.append(ast.literal_eval(p))
                    except Exception:
                        params.append(None)
            self.entries.append((self.file_path, node.lineno, cmd, params))
        self.generic_visit(node)


def parse_scripts(root):
    entries = []
    for dirpath, _, files in os.walk(root):
        for fname in files:
            if fname.endswith('.py'):
                fpath = os.path.join(dirpath, fname)
                try:
                    with open(fpath, encoding='utf-8') as f:
                        src = f.read()
                    tree = ast.parse(src)
                except Exception:
                    continue
                visitor = CmdVisitor(fpath)
                visitor.visit(tree)
                entries.extend(visitor.entries)
    # Sort by file path then line number
    entries.sort(key=lambda x: (x[0], x[1]))
    return entries

if __name__ == '__main__':
    scripts_root = 'Rosewood--RL_WHL_FULL3/scripts'
    seq = parse_scripts(scripts_root)
    for path, line, cmd, params in seq:
        print(f"{path}:{line}  {cmd}  {params}") 