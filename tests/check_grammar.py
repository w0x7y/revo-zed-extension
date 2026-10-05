"""Verify the grammar actually pinned by the extension, without modifying it.

Usage: python3 tests/check_grammar.py [path/to/tree-sitter-revo]
Requires Python 3.11+, Git, Tree-sitter CLI 0.26.9 and a C compiler.
"""

import sys

from grammar_support import grammar, run_checks


if __name__ == "__main__":
    if len(sys.argv) > 2:
        raise SystemExit(__doc__)
    with grammar(sys.argv[1] if len(sys.argv) == 2 else None) as parser:
        run_checks(parser)
    print("PASS: manifest-pinned grammar, corpus, canonical ASTs, current syntax and all Zed queries")
