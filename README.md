A BNF (Backus-Naur Form) parser and a LL input sequence scanner with backtracking

BNF syntax:
===========

1. non-terminals between `<>`
2. rules end at newline `\n`
3. assign with `::=`
4. operators:
	* alternative derivations separated by `|`
	* group items between `()`
	* optional items between `{}` or with postfix `?` operator
	* zero or more repetitions with postfix `*` operator
	* one or more repetitions with postfix `+` operator
5. set of terminal values between `[]`: in set `[aeiou]`, not in set `[^aeiou]` or ranges `[a-z]`

The BNF compiler uses a LL parser with backtracking:

1. no left-recursion: `<X> :== <X> ...`
2. no `a+ a` alike sequences
3. longest rule first: rule `<X> ::= a | a b` must be replaced by `<X> ::= a b | a`
4. special chars `\\<>(){}[]|+*?:=` each must be quoted with `\\`

Grammar example for a python tuple of integer literals (`tuple.bnf`):

```bnf
<tuple> ::= \( <body> \) | \( \)
<body>  ::= <elem> <num> | <elem>
<elem>  ::= <num> , <elem> | <num> ,
<num>   ::= <dig> <num> | <dig>
<dig>   ::= [0-9]
```

Test if an input sequence matches the above grammar with:

```
echo -n "(12,34,)" | python3 -m bnf tuple.bnf
```

The printed result should be `True` or `False` whether
the input sequence is accepted by the grammar, or not, respectively.

Note: input sequence must not contain a newline (`\n`) if grammar does not support it (use `echo -n`)

Use the environment `DEBUG=1` for a verbose output
(`DEBUG=2` for a more verbose output):

```
echo -n "(12,34,)" | DEBUG=1 python3 -m bnf tuple.bnf
```

In interactive mode:
```
>>> from bnf import grammar, parse
>>> grammar("<tuple> ::= \( <body> \) | \( \)\n<body>  ::= <elem> <num> | <elem>\n<elem>  ::= <num> , <elem> | <num> ,\n<num>   ::= <dig> <num> | <dig>\n<dig>   ::= [0-9]\n")
>>> parse("(12,34,)")
```

EBNF syntax:
============

1. terminal symbols must be quoted between `""`: `"if"`
2. rules end with `;` not a newline

remaining rules are the same as for BNF syntax.

The tuple example in eBNF becomes (`tuple.ebnf`):

```bnf
tuple ::= '(' body ')' | '(' ')' ;
body  ::= elem num | elem ;
elem  ::= num ',' elem | num ',' ;
num   ::= dig num | dig ;
dig   ::= [0-9] ;
```

Test if an input sequence matches the above grammar with:

```
echo -n "(12,34,)" | python3 -m ebnf tuple.ebnf
```

In interactive mode:
```
>>> from ebnf import grammar, parse
>>> grammar("tuple ::= '(' body ')' | '(' ')' ;body  ::= elem num | elem ;elem  ::= num ',' elem | num ',' ;num   ::= dig num | dig ;dig   ::= [0-9] ;")
>>> parse("(12,34,)")
```

The bnf/ package includes:
==========================

* bnf.py: BNF parser and input sequence scanner
* ebnf.py: extended BNF parser and input sequence scanner

Documentation in the docs/ directory:

* tutorial.html: an introduction guide
* internals.html: bnf/ebnf routine description

Code examples:

* exs/: some demonstration examples

(C) prs, IST 2022
