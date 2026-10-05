"""Check real syntax captures against the grammar pinned in extension.toml.

Usage: python3 tests/check_highlights.py [path/to/tree-sitter-revo]
Requires Python 3.11+, Git, tree-sitter CLI and a C compiler.
"""

import sys

from grammar_support import ROOT, captures, grammar


if len(sys.argv) > 2:
    raise SystemExit(__doc__)
fixture = ROOT / "tests/highlights.rv"
with grammar(sys.argv[1] if len(sys.argv) == 2 else None) as parser:
    parsed = parser.parse(fixture, quiet=True)
    parsed.check_returncode()
    # Compile every query, including editor-specific outline/indent captures.
    for query in sorted((ROOT / "languages/revo").glob("*.scm")):
        result = parser.query(query, fixture)
        if result.returncode:
            raise SystemExit(f"{query.name}: {result.stderr or result.stdout}")
        if query.name == "highlights.scm":
            found = set(captures(result.stdout))
        elif query.name == "outline.scm":
            outline = captures(result.stdout)

lines = fixture.read_text().splitlines()

def capture(name, row, text):
    column = lines[row].index(text)
    return name, row, column, row, column + len(text)

expected = {
    capture("keyword", 0, "import"),
    capture("keyword", 1, "comp"),
    capture("keyword", 3, "yield"),
    capture("keyword", 8, "test"),
    capture("keyword", 11, "suite"),
    capture("variable.parameter", 2, "name"),
    capture("property", 6, "name"),
    capture("function", 9, "greet"),
    capture("variable", 12, "struct"),
    capture("keyword", 14, "spawn"),
    capture("keyword", 15, "match"),
    capture("type", 18, "state"),
}
missing = expected - found
if missing:
    raise SystemExit(f"Missing captures: {sorted(missing)}")
for capture_name, row, column, end_row, end_column in found:
    if capture_name == "comment.doc" and row <= 9 <= end_row:
        raise SystemExit("Test block code must not be highlighted as documentation")
    if capture_name == "variable.parameter" and row == 9:
        raise SystemExit("Call arguments must not be highlighted as parameter declarations")
if ("name", 18, 5, 18, 10) not in outline:
    raise SystemExit("Lowercase type aliases must appear in the outline")
print("PASS: all queries compile; current keywords, parameters, properties and test bodies")
