# Revo for Zed

A Zed language extension for [Revo](https://revo.lung.fyi/).
It recognizes `.rv` and `.revo` files, adds tree-sitter syntax highlighting,
and launches the Revolt language server supplied by your installed Revo
executable with `revo lsp`.

## How to install in Zed

Install this checkout as a local development extension.

### Prerequisites

- Install [Zed](https://zed.dev/download).
- Install [Revo](https://revo.lung.fyi/#get) and make `revo` available on your
  shell's `PATH`. Run `revo --help` in a terminal and check that `lsp` appears
  in its commands. The extension uses this installation of Revo.
- Install [Rust through rustup](https://rustup.rs/). Restart Zed afterward so
  it can find the new toolchain.

### Installation steps

Get a local checkout first:

```sh
git clone https://github.com/scout0773/revo-zed-extension.git
```

If you already have a checkout, use that folder.

1. Open Zed's command palette with `Ctrl+Shift+P` on Linux or Windows, or
   `Cmd+Shift+P` on macOS.
2. Run `zed: install dev extension`. You can also open the Extensions page
   and click **Install Dev Extension**.
3. Select the extension's root folder, the one containing `extension.toml`
   and `Cargo.toml`.
4. Wait for the build to finish. Zed compiles the Rust adapter and downloads
   the tools needed to build the pinned tree-sitter grammar. The first
   installation needs internet access.
5. Open a Revo project or the included `connection-check.rv` file. Trust
   the project folder if Zed prompts you; the language server waits until
   that folder is trusted.

Zed manages the `wasm32-wasip2` target when Rust is installed through rustup
and downloads the grammar's WASI SDK automatically. See
[Zed's development extension documentation](https://zed.dev/docs/extensions/developing-extensions).

### Check that it works

The file's language should show **Revo** in Zed's status bar, and its code
should have syntax highlighting. In `connection-check.rv`, hover over
`greet` in the final line to check that the language server responds.

If it does not work, run `zed: open log` and look for messages mentioning
`revo` or `revolt`. If Zed cannot find the Revo executable, set its absolute
path using the settings in [Configure](#configure). If the extension build
fails, check that Rust is installed through rustup and retry the installation.

## Configure

The default command is `revo lsp`. To select a different executable, add the
following to Zed's settings, replacing the example path. Include
`"arguments": ["lsp"]` whenever you set `binary.path`, because Zed launches
explicit paths directly without using the extension's default arguments.
Merge these entries into any existing `lsp` and `languages` settings:

```json
{
  "lsp": {
    "revolt": {
      "binary": {
        "path": "/absolute/path/to/revo",
        "arguments": ["lsp"]
      }
    }
  },
  "languages": {
    "Revo": {
      "language_servers": ["revolt"],
      "semantic_tokens": "combined"
    }
  }
}
```

Zed also applies `lsp.revolt.binary.env` and any explicit arguments. The
extension supplies only the default executable lookup and `lsp` argument.

## Develop

- `src/lib.rs`: locates Revo and supplies the language server command.
- `extension.toml`: registers the language server and pins the grammar.
- `languages/revo/config.toml`: file associations, comments and brackets.
- `languages/revo/highlights.scm`: syntax highlighting queries.
- `languages/revo/overrides.scm`: string and comment scopes for quote closing.
- `languages/revo/indents.scm`: indentation for blocks, tables and parameters.
- `languages/revo/outline.scm`: named functions, procedural macros, types and tests.
- `languages/revo/brackets.scm`: matching delimiters and `do`/`end` blocks.
- `connection-check.rv`: a sample file for checking the connection.

To rebuild the Rust adapter from this directory:

```sh
rustup target add wasm32-wasip2
cargo build --locked --release --target wasm32-wasip2
cp target/wasm32-wasip2/release/revo_zed.wasm extension.wasm
```

Restart Zed after replacing the compiled adapter. Installing this directory
through `zed: install dev extension` also builds the grammar, which is sourced
from the [maintained Revo grammar](https://github.com/w0x7y/tree-sitter-revo)
at the revision recorded in `extension.toml`. Highlight queries are adapted
from that grammar's `queries/highlights.scm`.

To check the syntax scopes, install Python 3.11+, Git, the tree-sitter CLI
0.26.9 and a C compiler, then run:

```sh
python3 tests/check_scopes.py
python3 tests/check_highlights.py
python3 tests/check_grammar.py
python3 tests/check_grammar_support.py
```

The check fetches the grammar revision from `extension.toml` into a temporary
directory, parses real Revo strings and comments, and verifies the scope
captures used by quote closing. To reuse an existing checkout of that same
revision, pass its path as an argument.

The highlight check also compiles every Zed query and checks imports,
`comp`, `yield`, table fields, test bodies, parameter declarations and lowercase
type outlines. `check_grammar.py` runs the complete corpus and AST contracts
against the manifest pin. Each check uses a private parser library, shared
within that check, so parallel runs cannot overwrite a common cache.
The support regression uses the real CLI to check concurrent contexts, cleanup,
revision and dirty-input rejection, and syntax errors versus tool failures.

## Current Revo support

Revolt is bundled into Revo; updating the `revo` executable updates the
language server used by Zed. Verify it with `revo version`.
Current upstream source requires **Zig 0.17.0** and builds with
`zig build -Doptimize=safe`. See [Revo's build instructions](https://github.com/if-not-nil/revo#install-from-source)
and the [grammar coverage report](docs/grammar-continuation.md).

The current server provides completion, hover, definitions, references,
rename, document/workspace symbols, diagnostics, semantic tokens, inlay hints,
signature help and match quick fixes. It does not advertise a formatter.
New standard-library APIs come from the installed compiler; the extension
does not keep a separate list of builtins.

The manifest pins a public, immutable commit in
[w0x7y/tree-sitter-revo](https://github.com/w0x7y/tree-sitter-revo), which
preserves doomy's upstream history and attribution. It covers current generic
calls and types, structural function signatures, variadic type parameters,
imports, matches, postfix expressions, iterator ranges and macro calls.
The reviewed grammar passes 132 corpus cases and all 55 supported compiler
fixtures; one historical issue fixture contains compiler-rejected syntax.
See the [coverage report](docs/grammar-continuation.md) for the exact revisions
and the remaining approximation in general operator precedence.

[patches/tree-sitter-revo.patch](patches/tree-sitter-revo.patch) reproduces the
source changes against the original upstream base in `tests/compatibility.toml`.
It is already included in the public pin; do not apply it to that commit again.
To verify the original-base reproduction, use Python 3.11+, Node.js, Git,
Tree-sitter CLI 0.26.9 and a C compiler:

```sh
python3 tests/check_grammar_patch.py
```

That check generates the parser, runs the original and added corpus, verifies
AST contracts, and compiles all Zed queries. Normal extension installation
now builds the same published grammar rather than replacing locally patched
syntax support with an older parser.

## License

MIT. See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES)
for the grammar query attribution.

## Remove

Uninstall Revo from Zed's Extensions page and remove any `lsp.revolt` and
`languages.Revo` settings you added. The source repository remains available.

## Credits

Revo is maintained by [if-not-nil](https://github.com/if-not-nil/revo).
The maintained grammar preserves [doomy's original grammar](https://codeberg.org/doomy/tree-sitter-revo) and MIT attribution.
