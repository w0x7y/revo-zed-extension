# revo for zed

[revo](https://revo.lung.fyi) in [zed](https://zed.dev).

syntax highlighting for `.rv` and `.revo` files.
completion, hover, diagnostics, go to definition, and rename through revolt,
the language server bundled with revo.

## install

you need [zed](https://zed.dev/download), [revo](https://revo.lung.fyi/#get),
and [rust through rustup](https://rustup.rs). restart zed after installing rust.

```sh
# check that revo is on your PATH and lists the lsp command
revo --help

git clone https://github.com/w0x7y/revo-zed-extension.git
```

in zed:

1. open zed's command palette, `Ctrl+Shift+P` or `Cmd+Shift+P` on macOS
2. run `zed: install dev extension`
3. select the cloned `revo-zed-extension` folder
4. wait for the build, then open a `.rv` or `.revo` file. trust the project if asked

zed builds the extension and grammar for you. the first install needs internet.

## try it

try opening [connection-check.rv](connection-check.rv):

```revo
fn greet(name: string) -> string do
  "Hello, " ~ name
end

print(greet("Zed"))
```

look for `Revo` in the status bar and colors in the code.
hover over `greet` on the last line to check revolt.

## settings

the extension runs `revo lsp` from your project's `PATH`.
if zed can't find it, add this to your zed settings:

```json
{
  "lsp": {
    "revolt": {
      "binary": {
        "path": "/absolute/path/to/revo",
        "arguments": ["lsp"]
      }
    }
  }
}
```

replace the path with your revo executable. keep `"arguments": ["lsp"]`;
zed doesn't add it when you set a path. `lsp.revolt.binary.env` sets environment variables.

update revo to update revolt. check your version with `revo version`.
revolt doesn't provide a formatter.

## if something breaks

- no revolt? check that `revo --help` lists `lsp` and the project is trusted.
  try setting the path above
- build failed? install rust through rustup, restart zed, and try again
- still stuck? run `zed: open log`, look for `revo` or `revolt`, and include
  those messages in an [issue](https://github.com/w0x7y/revo-zed-extension/issues)

to uninstall, remove revo from zed's extensions page and delete any
`lsp.revolt` or `languages.Revo` settings you added.

## develop

the adapter is in [src/lib.rs](src/lib.rs), the grammar revision is in
[extension.toml](extension.toml), and the queries are in [languages/revo](languages/revo).
use `zed: install dev extension` to build both the adapter and grammar.
see [zed's extension docs](https://zed.dev/docs/extensions/developing-extensions).

to build just the adapter:

```sh
rustup target add wasm32-wasip2
cargo build --locked --release --target wasm32-wasip2
cp target/wasm32-wasip2/release/revo_zed.wasm extension.wasm
```

restart zed afterward.

the [grammar report](docs/grammar-continuation.md) has the check commands and
known limitations. checks need python 3.11+, git, tree-sitter CLI 0.26.9, and
a C compiler. the patch check also needs node.js. the pinned grammar already
includes the patch.

## credits

original extension by [scout0773](https://github.com/scout0773),
with updates by [w0x7y](https://github.com/w0x7y). licensed as [MIT](LICENSE).

syntax queries adapted from [doomy's tree-sitter-revo](https://codeberg.org/doomy/tree-sitter-revo),
with the maintained grammar at [w0x7y/tree-sitter-revo](https://github.com/w0x7y/tree-sitter-revo).
see [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES) for attribution.
