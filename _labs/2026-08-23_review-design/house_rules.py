#!/usr/bin/env python3
"""自チームの規約を機械に落とした3ルール。ruff/mypy が黙る層を拾う。"""
import ast
import sys

DB = ("fetch", "find", "query", "select", "get")
LOGGERS = ("log", "logger", "logging")
SECRET = ("token", "secret", "password", "authorization")
MONEY = ("price", "total", "subtotal", "fee", "amount", "yen")


def name_of(node):
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return ""


def root_of(node):
    while isinstance(node, ast.Attribute):
        node = node.value
    return node.id if isinstance(node, ast.Name) else ""


class Rules(ast.NodeVisitor):
    def __init__(self):
        self.hits = []
        self.depth = 0

    def _loop(self, node):
        self.depth += 1
        self.generic_visit(node)
        self.depth -= 1

    visit_For = _loop
    visit_While = _loop

    def visit_Call(self, node):
        fn = name_of(node.func)
        # HR01: ループの中でデータ取得を呼んでいる
        if self.depth and any(fn.startswith(p) for p in DB):
            self.hit(node, "HR01", "ループ内でDB取得")
        # HR02: ログに秘密を渡している
        if root_of(node.func) in LOGGERS:
            for a in node.args:
                if any(s in name_of(a).lower() for s in SECRET):
                    self.hit(node, "HR02", "ログに秘密を渡した")
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        self.money(node.target, node.annotation)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        r = node.returns
        if any(m in node.name.lower() for m in MONEY):
            self.money(node, r, node.name)
        self.generic_visit(node)

    def money(self, node, ann, nm=None):
        nm = nm or name_of(node)
        if ann is not None and name_of(ann) == "float":
            if any(m in nm.lower() for m in MONEY):
                self.hit(node, "HR03", "金額が float")

    def hit(self, node, code, msg):
        self.hits.append((node.lineno, code, msg))


def main(path):
    tree = ast.parse(open(path).read())
    r = Rules()
    r.visit(tree)
    for line, code, msg in sorted(set(r.hits)):
        print(f"{path}:{line} {code} {msg}")
    print(f"-- {len(set(r.hits))} 件")


if __name__ == "__main__":
    main(sys.argv[1])
