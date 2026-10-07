# revo-zed-extension

[revo](https://revo.lung.fyi) in [zed](https://zed.dev).

syntax highlighting for `.rv` and `.revo`, plus revolt, the language server
bundled with revo. completion, hover, diagnostics, definitions, rename, and more.

[get started](#get-started) | [settings](#settings) | [if something breaks](#if-something-breaks) | [develop](#develop) | [credits](#credits)

## get started

you need [zed](https://zed.dev/download), [revo](https://revo.lung.fyi/#get),
and [rust through rustup](https://rustup.rs). restart zed after installing rust.

```sh
# revo needs to be on your PATH, with the lsp command available
revo --help

git clone https://github.com/w0x7y/revo-zed-extension.git
```

install this checkout as a development extension:

1. open zed's command palette, `Ctrl+Shift+P` or `Cmd+Shift+P` on macOS
2. run `zed: install dev extension`
3. select the cloned `revo-zed-extension` folder, the one with `extension.toml` in it
4. wait for the build. the first install downloads tools and needs internet
5. open a `.rv` or `.revo` file. trust the project if zed asks

zed builds the rust adapter and the pinned grammar for you. with rustup installed,
it also manages the WebAssembly target. see [zed's extension docs](https://zed.dev/docs/extensions/developing-extensions).

try opening [connection-check.rv](connection-check.rv):

```revo
fn greet(name: string) -> string do
  "Hello, " ~ name
end

print(greet("Zed"))
```

the status bar should say `Revo`, and the code should have colors.
hover over `greet` on the last line to check the language server too.

## settings

by default, the extension finds `revo` on your project's `PATH` and runs `revo lsp`.
to use a different executable, merge this into your zed settings:

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

keep `"arguments": ["lsp"]` when setting `binary.path`.
zed launches explicit paths directly, so the default argument won't be added.
`lsp.revolt.binary.env` works too.

revolt ships with revo. update your `revo` executable to update the server;
`revo version` tells you what you have installed. the server doesn't advertise a formatter.

## if something breaks

- no language server? check that `revo --help` lists `lsp`, and that the project
  is trusted. set the executable path above if zed can't find it
- build failed? check that rust is installed through rustup, restart zed, and
  try installing the extension again
- still stuck? run `zed: open log` and look for `revo` or `revolt`.
  include those messages when [opening an issue](https://github.com/w0x7y/revo-zed-extension/issues)

to remove it, uninstall revo from zed's extensions page and remove any
`lsp.revolt` and `languages.Revo` settings you added.

## develop

the rust adapter is in [src/lib.rs](src/lib.rs), the grammar pin is in
[extension.toml](extension.toml), and the editor queries are in
[languages/revo](languages/revo).

<details>
<summary>build the adapter</summary>

```sh
rustup target add wasm32-wasip2
cargo build --locked --release --target wasm32-wasip2
cp target/wasm32-wasip2/release/revo_zed.wasm extension.wasm
```

restart zed afterward. installing through `zed: install dev extension` also
builds the grammar.

</details>

<details>
<summary>run the checks</summary>

you need python 3.11+, git, tree-sitter CLI 0.26.9, and a C compiler.

```sh
python3 tests/check_scopes.py
python3 tests/check_highlights.py
python3 tests/check_grammar.py
python3 tests/check_grammar_support.py
```

these fetch the pinned grammar into temporary directories. they check scopes,
all zed queries, the grammar corpus, AST contracts, and parser cleanup and errors.
you can pass a clean checkout of the same grammar revision to reuse it.

to check that the source patch reproduces the grammar from its original upstream
base, you also need node.js:

```sh
python3 tests/check_grammar_patch.py
```

the patch is already included in the public grammar pin. don't apply it there again.
the [coverage report](docs/grammar-continuation.md) records the tested revisions
and remaining grammar limitations.

</details>

## credits

original extension by [scout0773](https://github.com/scout0773),
with updates by [w0x7y](https://github.com/w0x7y). licensed as [MIT](LICENSE).

syntax queries adapted from [doomy's tree-sitter-revo](https://codeberg.org/doomy/tree-sitter-revo),
with the maintained grammar at [w0x7y/tree-sitter-revo](https://github.com/w0x7y/tree-sitter-revo).
see [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES) for attribution.
