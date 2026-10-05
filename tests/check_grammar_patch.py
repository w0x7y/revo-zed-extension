"""Reconstruct and verify the source patch on its original upstream revision.

Usage: python3 tests/check_grammar_patch.py [path/to/tree-sitter-revo]
Requires Python 3.11+, Git, Tree-sitter CLI 0.26.9, Node.js and a C compiler.
The supplied checkout is only a clone source and is never modified.
"""

import sys

from grammar_support import grammar, run_checks


if __name__ == "__main__":
    if len(sys.argv) > 2:
        raise SystemExit(__doc__)
    with grammar(sys.argv[1] if len(sys.argv) == 2 else None, patched=True) as parser:
        run_checks(parser)
    print("PASS: upstream patch reproduction, corpus, canonical ASTs, current syntax and all Zed queries")
