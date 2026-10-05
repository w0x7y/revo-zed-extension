(function
  "fn" @context
  name: (ident) @name) @item

(proc_macro
  "proc" @context
  name: (ident) @name) @item

(type_expression
  "type" @context
  type: [(type) (ident)] @name) @item

(test
  "test" @context
  name: (string) @name) @item
