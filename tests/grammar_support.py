"""Prepare immutable grammar inputs and verify their shared editor contracts.

Parser execution belongs to the grammar's test/ast/revo_parser.py module.
Published checks use extension.toml; patch reproduction uses its upstream base.
"""

from contextlib import contextmanager
import importlib.util
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]


def specification(patched=False):
    if patched:
        return tomllib.loads((ROOT / "tests/compatibility.toml").read_text())["grammar_patch"]
    return tomllib.loads((ROOT / "extension.toml").read_text())["grammars"]["revo"]


@contextmanager
def grammar(source=None, patched=False):
    """Yield the grammar-owned Parser with a private compiled library.

    Supplied published checkouts must match the manifest and have clean inputs.
    Patch reproduction always clones first, leaving supplied checkouts untouched.
    """
    spec = specification(patched)
    with tempfile.TemporaryDirectory(prefix="revo-grammar-") as directory:
        if source is not None and not patched:
            checkout = Path(source).resolve()
            revision = subprocess.check_output(
                ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True,
            ).strip()
            if revision != spec["rev"]:
                raise SystemExit("Grammar checkout must match grammars.revo.rev in extension.toml")
            if subprocess.check_output(
                ["git", "-C", str(checkout), "status", "--porcelain", "-z", "--untracked-files=all", "--",
                 "grammar.js", "src", "tree-sitter.json", "package.json", "binding.gyp",
                 "test", "queries"],
            ):
                raise SystemExit("Grammar inputs must be clean; use check_grammar_patch.py for patched input")
        else:
            checkout = Path(directory) / "grammar"
            repository = str(Path(source).resolve()) if source is not None else spec["repository"]
            subprocess.run(
                ["git", "clone", "--quiet", "--no-hardlinks", repository, str(checkout)], check=True,
            )
            subprocess.run(
                ["git", "-C", str(checkout), "checkout", "--quiet", "--detach", spec["rev"]],
                check=True,
            )
        if patched:
            subprocess.run(
                ["git", "apply", str(ROOT / "patches/tree-sitter-revo.patch")],
                cwd=checkout, check=True,
            )
            subprocess.run(["tree-sitter", "generate"], cwd=checkout, check=True)

        module_path = checkout / "test/ast/revo_parser.py"
        module_spec = importlib.util.spec_from_file_location("revo_grammar_parser", module_path)
        module = importlib.util.module_from_spec(module_spec)
        sys.modules[module_spec.name] = module
        module_spec.loader.exec_module(module)
        with module.Parser(checkout) as parser:
            yield parser


def captures(output):
    """Read the CLI's capture names and zero-based source spans."""
    return [
        (name, int(row), int(column), int(end_row), int(end_column))
        for name, row, column, end_row, end_column in re.findall(
            r"capture: \d+ - ([\w.]+), start: \((\d+), (\d+)\), end: \((\d+), (\d+)\)",
            output,
        )
    ]


def parsed_xml(result):
    """Return a real parse tree, or fail on CLI/infrastructure errors.

    Tree-sitter reports syntax errors with exit status 1 and a complete tree.
    Loading/read errors and crashes must never count as expected invalid syntax.
    """
    if result.returncode not in (0, 1) or "</sources>" not in result.stdout:
        raise RuntimeError(f"Tree-sitter did not produce a parse tree: {result.stderr or result.stdout}")
    try:
        tree = ET.fromstring(result.stdout.split("</sources>", 1)[0] + "</sources>")
    except ET.ParseError as error:
        raise RuntimeError(f"Tree-sitter produced malformed XML: {result.stderr or result.stdout}") from error
    source = tree.find("source")
    if tree.tag != "sources" or source is None or not len(source) or "srow" not in source[0].attrib:
        raise RuntimeError("Tree-sitter output contains no source parse tree")
    # CLI 0.26.9 omits missing-token attributes from XML, but reports them in
    # its parse summary after the XML document (including unnamed tokens).
    summary = result.stdout.split("</sources>", 1)[1]
    has_error = bool(list(tree.iter("ERROR"))) or "(MISSING " in summary
    if bool(result.returncode) != has_error:
        raise RuntimeError(f"Tree-sitter status {result.returncode} disagrees with its syntax tree")
    return tree


def run_checks(parser):
    """Check corpus, canonical AST contracts, current syntax and every Zed query."""
    checkout = parser.grammar
    subprocess.run(
        ["tree-sitter", "test", "--lib-path", str(parser.library), "--lang-name", "revo"],
        cwd=checkout, env=parser.env, check=True,
    )
    subprocess.run(
        [sys.executable, str(checkout / "test/ast/check_generic_calls.py"), str(checkout),
         str(ROOT / "languages/revo/highlights.scm"), str(checkout / "queries/highlights.scm"),
         "--lib-path", str(parser.library)],
        env=parser.env, check=True,
    )
    subprocess.run(
        [sys.executable, str(checkout / "test/ast/check_expressions.py"), str(checkout),
         "--lib-path", str(parser.library)], env=parser.env, check=True,
    )
    fixture = ROOT / "tests/current-syntax.rv"
    result = parser.parse(fixture, xml=True)
    tree = parsed_xml(result)
    if result.returncode:
        raise SystemExit(f"Current syntax must parse cleanly: {result.stdout}")
    lines = fixture.read_text().splitlines()
    call_line = "let explicit = identity<num>(2)"
    call_row = lines.index(call_line)
    call_column = call_line.index("identity")
    if not any(
        node.get("srow") == str(call_row) and node.get("scol") == str(call_column)
        and node.get("erow") == str(call_row) and node.get("ecol") == str(len(call_line))
        for node in tree.iter("function_call")
    ):
        raise SystemExit("Explicit generic syntax must parse as a function_call, not comparisons")
    for query in sorted((ROOT / "languages/revo").glob("*.scm")):
        result = parser.query(query, fixture)
        if result.returncode:
            raise SystemExit(f"{query.name}: {result.stderr or result.stdout}")
        if query.name == "highlights.scm":
            declaration_row = lines.index("fn lower<t,>(value: t) -> t value")
            found = captures(result.stdout)
            for row, column in ((declaration_row, 3), (call_row, call_column)):
                names = sorted((start, end) for name, start_row, start, end_row, end in found
                               if name == "function" and start_row == row)
                expected = "lower" if row == declaration_row else "identity"
                if names != [(column, column + len(expected))]:
                    raise SystemExit(f"Only the function name may have a function capture on row {row}, got {names}")
