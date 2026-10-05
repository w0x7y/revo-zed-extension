"""Parse all tracked Revo fixtures at the audited compiler revision.

Usage: python3 tests/check_compiler_syntax.py GRAMMAR COMPILER
GRAMMAR must be a clean checkout of the extension's published pin.
Requires Python 3.11+, Git, Tree-sitter CLI 0.26.9 and a C compiler.
This checks syntax coverage; it does not execute examples or prove AST equivalence.
"""

from pathlib import Path
import subprocess
import sys
import tomllib

from grammar_support import grammar, parsed_xml


def verify(parser, compiler):
    compiler = Path(compiler).resolve()
    spec = tomllib.loads(Path(__file__).with_name("compatibility.toml").read_text())["compiler"]
    revision = subprocess.check_output(
        ["git", "-C", str(compiler), "rev-parse", "HEAD"], text=True,
    ).strip()
    if revision != spec["rev"]:
        raise SystemExit("Compiler checkout must match tests/compatibility.toml")
    subprocess.run(
        ["git", "-C", str(compiler), "diff", "--exit-code", "HEAD", "--", "*.rv"],
        check=True, capture_output=True,
    )
    files = subprocess.check_output(
        ["git", "-C", str(compiler), "ls-files", "-z", "--", "*.rv"],
    ).decode().rstrip("\0").split("\0")
    if not files or not files[0]:
        raise SystemExit("Compiler checkout contains no tracked Revo fixtures")
    expected_invalid = spec.get("expected_invalid", {})
    if set(expected_invalid) - set(files):
        raise SystemExit("Expected-invalid fixtures must exist in the audited compiler checkout")
    failures = []
    for filename in files:
        result = parser.parse(compiler / filename, xml=True)
        try:
            parsed_xml(result)
        except RuntimeError as error:
            failures.append(f"{filename}: CLI/infrastructure failure: {error}")
            continue
        if filename in expected_invalid:
            if not result.returncode:
                failures.append(f"{filename}: expected invalid syntax to remain visibly errored")
            else:
                print(f"KNOWN INVALID: {filename}: {expected_invalid[filename]}")
        elif result.returncode:
            failures.append(f"{filename}: {result.stdout.strip() or result.stderr.strip()}")
    if failures:
        raise SystemExit(f"{len(failures)}/{len(files)} fixtures failed:\n" + "\n".join(failures))
    print(f"PASS: {len(files) - len(expected_invalid)} compiler fixtures parse clean; "
          f"{len(expected_invalid)} known-invalid fixture accounted for")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    with grammar(sys.argv[1]) as parser:
        verify(parser, sys.argv[2])
