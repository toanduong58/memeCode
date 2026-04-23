# MemeCode

<p align="center">
  <img src="docs/memecode_logo.svg" alt="MemeCode language logo" width="480"/>
</p>

## Language overview

**MemeCode** is a small educational programming language with meme-themed keywords. The implementation follows a classic pipeline: **lexer → parser → abstract syntax tree (AST) → interpreter**, matching the structure typically used when teaching compilers and formal grammars.

The language includes typed variable declarations, `yapping` for output, conditionals (`bet` / `lowkey` / `nahFr`), comparisons, and boolean logic (`&&`, `||`). Line comments begin with `#`. There are no user-defined functions in the current version; control flow and expressions are otherwise similar in spirit to a restricted subset of Python.

**How to run:** from the project directory,

```bash
python interpreter.py yourfile.memecode
```

The interpreter will display the AST followed by the program output.

---

## Example program

Below is a valid `.memecode` sample showing **comments**, **variables**, **types**, **printing**, **conditionals**, and **boolean / comparison** expressions:

```text
# Demo: variables, logic, and branching
lore msg = "MemeCode says hi"
sixSeven n = 3
vibeCheck ok = n > 1 && n < 10
losing5050 pi = 3.14

yapping(msg)
yapping(ok)
yapping(pi)

bet ok == noCap {
    yapping("logic checks out")
} lowkey n == 0 {
    yapping("zero")
} nahFr {
    yapping("other case")
}
```

---

## Full syntax table

MemeCode keyword or symbol (left) and its role (right).

| Syntax | Meaning |
|--------|---------|
| `yapping(expr)` | Print a single expression (like `print` in Python). |
| `lore` | String type; initializer must be a string literal. |
| `sixSeven` | Integer type; initializer must be an integer literal. |
| `losing5050` | Float type; initializer must be a float literal. |
| `vibeCheck` | Boolean type; initializer is a boolean expression. |
| `noCap` | Boolean literal **true**. |
| `cap` | Boolean literal **false**. |
| `=` | Assignment in declarations: `type name = expr`. |
| `bet` | Start conditional (`if`). |
| `lowkey` | Else-if branch (`elif`). |
| `nahFr` | Else branch (`else`). |
| `{` `}` | Block delimiters around statement lists. |
| `==` `!=` `<` `>` `<=` `>=` | Comparison operators. |
| `&&` `||` | Logical **and** / **or**. |
| `#` … end of line | Line comment (ignored by the lexer). |

---

## Grammar (EBNF)

The following **extended BNF** describes MemeCode's concrete syntax. Notation: `|` alternation, `[ … ]` zero or one, `{ … }` zero or more, `"…"` terminals.

```ebnf
(* 1. Program *)
program     ::= { statement } EOF ;

(* 2. Top-level statements *)
statement   ::= print_stmt | decl_stmt | if_stmt ;

(* 3. Print *)
print_stmt  ::= "yapping" "(" expr ")" ;

(* 4-5. Typed declaration *)
decl_stmt   ::= type identifier "=" expr ;
type        ::= "lore" | "sixSeven" | "vibeCheck" | "losing5050" ;

(* 6-8. Conditional with optional else-if and else *)
if_stmt     ::= "bet" expr block { elseif_part } [ else_part ] ;
elseif_part ::= "lowkey" expr block ;
else_part   ::= "nahFr" block ;

(* 9. Block *)
block       ::= "{" { statement } "}" ;

(* 10-12. Expressions *)
expr        ::= primary { binary_op primary } ;
binary_op   ::= "&&" | "||" | "==" | "!=" | "<" | ">" | "<=" | ">=" ;

(* 13-14. Primary *)
primary     ::= literal | identifier ;
literal     ::= string | integer | float | bool_lit ;
bool_lit    ::= "noCap" | "cap" ;
```

*Lexical notes:* `identifier` is a letter or underscore followed by letters, digits, or underscores; `string` is characters between `"` … `"`; `integer` is one or more digits; `float` is digits containing a decimal point; whitespace separates tokens; `#` starts a comment to end of line.

---

## Group members

| # | Full name |
|---|-----------|
| 1 | Duong Thanh Toan |
