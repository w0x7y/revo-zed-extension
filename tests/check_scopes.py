"""Check quote-exclusion scopes against the actual pinned Revo grammar.

Usage: python3 tests/check_scopes.py [path/to/tree-sitter-revo]
Requires Python 3.11+, Git, the tree-sitter CLI and a C compiler.
Without a grammar path, fetch the pinned grammar into a temporary directory.
"""

import sys
import tempfile
from pathlib import Path

from grammar_support import ROOT, captures, grammar


query = ROOT / "languages/revo/overrides.scm"
fixture = ROOT / "tests/scopes.rv"
if len(sys.argv) > 2:
    raise SystemExit(__doc__)

with grammar(sys.argv[1] if len(sys.argv) == 2 else None) as parser:
    with tempfile.TemporaryDirectory(prefix="revo-scopes-") as directory:
        scratch_query = Path(directory) / "overrides.scm"
        # Zed has no exclusions when the overrides query is absent.
        scratch_query.write_text(query.read_text() if query.exists() else "")
        result = parser.query(scratch_query, fixture)
        result.check_returncode()

found = set(captures(result.stdout))
expected = {
    ("string", 0, 11, 0, 18),
    ("comment.inclusive", 1, 0, 1, 25),
    ("comment.inclusive", 2, 0, 2, 35),
    ("comment.inclusive", 3, 0, 3, 33),
    ("comment.inclusive", 4, 0, 4, 40),
}
if found != expected:
    raise SystemExit(f"Scope mismatch: missing {expected - found}, unexpected {found - expected}")
print("PASS: string, line comment, block comment, documentation and module documentation scopes")
