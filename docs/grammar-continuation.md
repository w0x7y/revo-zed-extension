# Current Revo grammar coverage

The maintained grammar is published at
[w0x7y/tree-sitter-revo](https://github.com/w0x7y/tree-sitter-revo), with all
54 upstream commits retained and an MIT license crediting doomy, contributors
and Idan Gilboa. `extension.toml` pins the reviewed public commit
[`cd1bed33767f7dbfbfbc7882e4a18d5ec229030b`](https://github.com/w0x7y/tree-sitter-revo/commit/cd1bed33767f7dbfbfbc7882e4a18d5ec229030b),
updated from `f15165b5391656ed3dcce25e18dbfba4320d80ed`.

The audit uses Revo compiler commit
[`e94e6d89ddaabb3249b38c1b10df87c700d1e8dc`](https://github.com/if-not-nil/revo/commit/e94e6d89ddaabb3249b38c1b10df87c700d1e8dc)
and Tree-sitter CLI 0.26.9. The original upstream grammar base is
`610fa6a4ff0fecd9cc81806e5e85ea61c92091b4`.

## Verified coverage

All 55 supported checked-in compiler `.rv` fixtures parse without errors,
up from 23 with the original grammar and 34 with the preceding local patch.
The remaining `issues/match.rv` fixture contains unfinished `..rest` table
patterns and range match patterns. The current compiler rejects both; the
fixture explicitly marks them unfinished. The grammar retains its error,
and `tests/compatibility.toml` records this exception rather than silently
excluding it from the result.

The compiler audit and public grammar pin were refreshed on 2026-10-09.
The grammar rejects whitespace before a loop range separator, including complete
programs such as `for i in 0 ..3 do i end` and
`for i in 0..2 ..10 do i end`, following Revo's
[range-start and step adjacency checks](https://github.com/if-not-nil/revo/commit/71115dea59391f2fbb1e5e79226157aea3a6ffd5).
Strings stay opaque syntax nodes, so `"#{t:d}"` remains highlighted as a string
while [the compiler reports an invalid interpolation mode](https://github.com/if-not-nil/revo/commit/e94e6d89ddaabb3249b38c1b10df87c700d1e8dc).
The supported modes are `:v`, `:?` and `:p`; `"#{:d}"` remains valid because
its expression is a lone atom. Comment extras can also bridge a loop range
operator, as in `start##gap##..limit`, although the compiler requires literal
adjacency. These are intentional editor recoveries; Revolt supplies compiler
diagnostics.

Range bounds now use expression nodes for every numeric spelling, retaining the
named `range` node. Arithmetic stays within its start, step or endpoint, and
table index slices support computed and omitted bounds. Numeric bounds have
children rather than the opaque tokens used by the preceding public pin.
The existing Zed queries compile against these structures, preserving numeric
constant captures and variable captures in computed bounds.

The pinned public grammar passes 188 corpus cases, including complete-program
range and interpolation regressions with explicit editor recovery expectations.
Separate checks verify 25 expression forms, 18 valid generic calls and 21 rejected
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
and qualified macro calls with empty or trailing argument lists.

## Compiler contracts

Ordinary calls require adjacent argument parentheses. Generic calls also
require adjacent `<` and `>(`, an identifier-only type list within the
compiler's 32-token lookahead, and a complete bare or dotted name receiver.
Indexed, called or numeric-field receivers retain comparison parsing.
Comments and ASCII whitespace can separate dotted path segments; comments
inside generic arguments stop speculation. Keyword field names are allowed,
while bare keyword receivers and keyword generic arguments are rejected.
Sources: [postfix parsing](https://github.com/if-not-nil/revo/blob/e94e6d89ddaabb3249b38c1b10df87c700d1e8dc/src/lang/Parser.zig#L287),
[generic speculation](https://github.com/if-not-nil/revo/blob/e94e6d89ddaabb3249b38c1b10df87c700d1e8dc/src/lang/Parser.zig#L1634),
[type syntax](https://github.com/if-not-nil/revo/blob/e94e6d89ddaabb3249b38c1b10df87c700d1e8dc/src/lang/type_syntax.zig),
[identifier characters](https://github.com/if-not-nil/revo/blob/e94e6d89ddaabb3249b38c1b10df87c700d1e8dc/src/lang/Lexer.zig#L1067).

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
