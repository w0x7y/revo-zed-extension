"""Exercise private parser ownership and invalid-input failures with the real CLI.

Usage: python3 tests/check_grammar_support.py [path/to/tree-sitter-revo]
Requires the manifest-pinned grammar, Git, Tree-sitter CLI 0.26.9 and a C compiler.
"""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys
import tempfile

from grammar_support import ROOT, grammar, parsed_xml, specification


def rejected(checkout, message):
    try:
        with grammar(checkout):
            raise AssertionError("Invalid grammar checkout was accepted")
    except SystemExit as error:
        assert message in str(error), error


def verify(source=None):
    with tempfile.TemporaryDirectory(prefix="revo-support-check-") as directory:
        scratch = Path(directory)
        fixture = scratch / "syntax.rv"
        fixture.write_text("identity<num>(2)\n")
        with grammar(source) as first:
            with grammar(first.grammar) as second:
                first_library, second_library = first.library, second.library
                assert first_library != second_library, "Contexts must own different parser libraries"
                assert first.env["XDG_CACHE_HOME"] != second.env["XDG_CACHE_HOME"], "CLI caches must be private"
                initial_stat = first_library.stat()
                with ThreadPoolExecutor(max_workers=2) as pool:
                    first_result = pool.submit(first.parse, fixture, xml=True)
                    second_result = pool.submit(second.query, ROOT / "languages/revo/highlights.scm", fixture)
                    assert not first_result.result().returncode
                    assert not second_result.result().returncode
                assert first_library.stat().st_mtime_ns == initial_stat.st_mtime_ns, "Parsing must reuse its library"
                assert first_library.stat().st_size == initial_stat.st_size

                fixture.write_text(":Ł\n")
                result = first.parse(fixture, xml=True)
                assert result.returncode == 1 and list(parsed_xml(result).iter("ERROR")), "Real syntax errors must remain visible"
                fixture.write_text("fn missing_end() do 1\n")
                result = first.parse(fixture, xml=True)
                assert result.returncode == 1
                parsed_xml(result)  # A missing unnamed token still has a real parse result.
                try:
                    parsed_xml(first.parse(scratch / "missing.rv", xml=True))
                except RuntimeError as error:
                    assert "did not produce a parse tree" in str(error)
                else:
                    raise AssertionError("Missing input must fail, never count as expected invalid syntax")

            assert not second_library.exists(), "Closing a context must delete its owned library"
            checkout = scratch / "checkout"
            subprocess.run(
                ["git", "clone", "--quiet", "--no-hardlinks", str(first.grammar), str(checkout)], check=True,
            )
            subprocess.run(
                ["git", "-C", str(checkout), "checkout", "--quiet", "--detach", specification()["rev"]], check=True,
            )
            for name in ("tree-sitter.json", "test/ast/check_generic_calls.py"):
                original = (checkout / name).read_text()
                (checkout / name).write_text(original + "\n")
                rejected(checkout, "inputs must be clean")
                (checkout / name).write_text(original)
            unexpected = checkout / "test/ast/untracked_source.py"
            unexpected.write_text("# This untracked source must not enter pinned verification.\n")
            rejected(checkout, "inputs must be clean")
            unexpected.unlink()
            subprocess.run(
                ["git", "-C", str(checkout), "checkout", "--quiet", "--detach", specification(patched=True)["rev"]],
                check=True,
            )
            rejected(checkout, "must match grammars.revo.rev")
        assert not first_library.exists(), "Closing a context must delete its owned library"
    print("PASS: concurrent private libraries, cleanup, library reuse, syntax/infrastructure failures and pinned-input rejection")


if __name__ == "__main__":
    if len(sys.argv) > 2:
        raise SystemExit(__doc__)
    verify(sys.argv[1] if len(sys.argv) == 2 else None)
