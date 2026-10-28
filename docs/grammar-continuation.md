# Current Revo grammar coverage

The maintained grammar is published at
[w0x7y/tree-sitter-revo](https://github.com/w0x7y/tree-sitter-revo), with all
54 upstream commits retained and an MIT license crediting doomy, contributors
and Idan Gilboa. `extension.toml` pins the reviewed public commit
[`f3e076048eef7bb55f5055df510fb54374a1050d`](https://github.com/w0x7y/tree-sitter-revo/commit/f3e076048eef7bb55f5055df510fb54374a1050d),
updated from `cd1bed33767f7dbfbfbc7882e4a18d5ec229030b`.

The audit uses Revo compiler commit
[`eefa192ea40d918d21630350219789e57fb6e661`](https://github.com/if-not-nil/revo/commit/eefa192ea40d918d21630350219789e57fb6e661)
and Tree-sitter CLI 0.26.9. It moved from
`e94e6d89ddaabb3249b38c1b10df87c700d1e8dc` to
`f0034ab75aaf49d65bc1b4769987f99380383fcb` on 2026-10-10, when upstream
changed only its README and wasm build defaults, to
`9c46813e054381b080ea8a3ea418247dd5912596` on 2026-10-13, when upstream
changed only its Nix flake, to
`c9ff2105656803359867a6f13213330ee672d898` on 2026-10-14, when upstream
changed only a README link, to
`1f95869439fe41da49aab0cce7fa94134ec5ddd4` on 2026-10-16, when
upstream enabled the LSP feature in its Nix package, to
`d2f16441c1554fec50d0098434223850bc4a1868` on 2026-10-17, when
upstream added LSP to its default native build features, to
`482ef26f80f7b7b88e3c4b74d20b914a00e6e5f6` on 2026-10-21, when
upstream added `dataframe.sort()` to its runtime library, to
`1060fcf44a16a185263b3cb244cca886ac017acc` on 2026-10-22, when upstream
added `dataframe.row()` and `dataframe.filter()`, and to the current commit
on 2026-10-28. None of the earlier moves changed the lexer or parser.
The current commit removes the `num` and `int` type aliases. Its parent,
[`8680d687a0ea04e1738c5d1e67ce0863134cc677`](https://github.com/if-not-nil/revo/commit/8680d687a0ea04e1738c5d1e67ce0863134cc677),
rewrites the lexer and parser around a concrete syntax tree and removes
macros.
The original upstream grammar base is `610fa6a4ff0fecd9cc81806e5e85ea61c92091b4`.

## Verified coverage

All 50 supported checked-in compiler `.rv` fixtures parse without errors.
On the same 51 fixtures the original grammar parses 22 and the preceding
local patch 50. The remaining `issues/match.rv` fixture contains unfinished
`..rest` table patterns and range match patterns. The current compiler
rejects `..rest` while parsing and range patterns while compiling; the
fixture explicitly marks both unfinished. The grammar retains its error,
and `tests/compatibility.toml` records this exception rather than silently
excluding it from the result.

The compiler audit and public grammar pin were refreshed on 2026-10-28.
`macro`, `proc` and `skip` are now ordinary names, so the grammar has no
macro, procedural macro or quasiquote nodes and a backtick is a syntax error;
`skip` still marks `test/skip`. A trailing `!` is part of an ordinary call
name, as in `fmt!()`, and names end with at most one `?` or `!`. Name atoms
stop at operators, so `:a-b` is `:a - b`. `num` and `int` parse as plain type
names. The Zed queries no longer capture the removed macro nodes.
The grammar rejects whitespace before a loop range separator, including complete
programs such as `for i in 0 ..3 do i end` and
`for i in 0..2 ..10 do i end`, following Revo's
[range-start and step adjacency checks](https://github.com/if-not-nil/revo/commit/71115dea59391f2fbb1e5e79226157aea3a6ffd5).
Interpolations are lexed as code, so nested strings, raw strings, braces and
comments inside `#{...}` stay within one string node, as in `"#{f("x")}"`.
`'...'` strings are raw, with no escapes.
Strings stay opaque syntax nodes, so `"#{t:d}"` remains highlighted as a string
while [the compiler reports an invalid interpolation mode](https://github.com/if-not-nil/revo/commit/e94e6d89ddaabb3249b38c1b10df87c700d1e8dc).
The supported modes are `:v`, `:?` and `:p`; `"#{:d}"` remains valid because
its expression is a lone atom. Comment extras can also bridge a loop range
operator, as in `start##gap##..limit`, although the compiler requires literal
adjacency. The grammar has no bare-call node, so chained bare-call arguments
such as `f "x" "y"` still parse. Keywords other than `type` and `import` are
no longer binding names or labels upstream (`let do = 1`, `do/end`), but the
grammar still reads them as names where no keyword is valid. Malformed
numbers such as `1__2` also still parse. These are intentional editor
recoveries; Revolt supplies compiler diagnostics.

Range bounds now use expression nodes for every numeric spelling, retaining the
named `range` node. Arithmetic stays within its start, step or endpoint, and
table index slices support computed and omitted bounds. Numeric bounds have
children rather than the opaque tokens used by pin
`f15165b5391656ed3dcce25e18dbfba4320d80ed`.
The existing Zed queries compile against these structures, preserving numeric
constant captures and variable captures in computed bounds.

The pinned public grammar passes 191 corpus cases, including complete-program
range and interpolation regressions with explicit editor recovery expectations.
Separate checks verify 25 expression forms, 19 valid generic calls and 22 rejected
generic-call forms, comparison trees, lexical nodes and function captures.
Unicode atom and receiver checks reject codepoints that could otherwise
narrow to ASCII in the external scanner. Both native and Wasm parser builds
pass. Independent fresh generation matches the committed parser, schemas
and C headers byte-for-byte.

Covered additions include structural and positional function types,
variadic signatures, nested generic applications, qualified/optional types,
contextual keyword fields, tagged unions, atom digit suffixes, grouped
imports, keyed match syntax, computed/open iterator ranges, unary and postfix
expressions, repeated/value calls, empty parentheses, labeled break values,
and qualified `!`-suffixed calls with empty or trailing argument lists.

## Compiler contracts

Ordinary calls require adjacent argument parentheses. Generic calls also
require adjacent `<` and `>(`, an identifier-only type list within the
compiler's 32-token lookahead, and a complete bare or dotted name receiver.
Indexed, called or numeric-field receivers retain comparison parsing.
Comments and ASCII whitespace can separate dotted path segments and generic
arguments; doc comments inside generic arguments stop speculation. Keyword
field names are allowed, while bare keyword receivers and keyword generic
arguments are rejected. The compiler also accepts a parenthesized path
receiver such as `(identity)<T>(2)`; the grammar keeps comparison parsing for
that form.
Sources: [postfix parsing](https://github.com/if-not-nil/revo/blob/eefa192ea40d918d21630350219789e57fb6e661/src/lang/Parser.zig#L630),
[generic speculation](https://github.com/if-not-nil/revo/blob/eefa192ea40d918d21630350219789e57fb6e661/src/lang/Parser.zig#L2177),
[type syntax](https://github.com/if-not-nil/revo/blob/eefa192ea40d918d21630350219789e57fb6e661/src/lang/type_syntax.zig),
[identifier characters](https://github.com/if-not-nil/revo/blob/eefa192ea40d918d21630350219789e57fb6e661/src/lang/Lexer.zig#L1110).

Type records and expression tables have separate hidden grammar rules but
retain the existing `table` and `field` tree nodes. This keeps contextual
record keywords from consuming expression statements such as labeled breaks.
Signature parameters likewise retain the existing `parameters` and
`parameter` nodes. Zed queries select field and function names
explicitly, preserving type and parameter captures.

The inherited operation tree remains flatter than the compiler's precedence
parser. Successful fixture parsing does not establish compiler-identical
ASTs or prove that historical examples execute or type-check. The targeted
AST checks establish the contracts listed above.

## Reproduce

The published grammar contains generated source and its AST checks:

```sh
python3 tests/check_scopes.py
python3 tests/check_highlights.py
python3 tests/check_grammar.py
python3 tests/check_grammar_support.py
python3 tests/check_grammar_patch.py
python3 tests/check_compiler_syntax.py /path/to/published-grammar /path/to/revo
```

The compiler checkout must match `tests/compatibility.toml`; the supplied
grammar checkout must be clean and match `extension.toml`. Generated parser
source is already committed in that public revision. The source patch applies to
its original Codeberg base, independently of the public manifest pin.
Zed installation builds the published grammar revision recorded in the manifest.
