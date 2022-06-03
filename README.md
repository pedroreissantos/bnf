A BNF (Backus-Naur Form) parser and a greedy LL input sequence scanner

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
5. set of terminal values between `[]`, not in set `[^...]` or ranges: `[a-z]`

Grammar example for a python tuple of integer literals:

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

Note: input sequence must not contain a newline (`\n`) if grammar does not support it (use `echo -n`)

Use the environment `DEBUG=1` for a verbose output:

```
echo -n "(12,34,)" | DEBUG=1 python3 -m bnf tuple.bnf
```

The BNF compiler uses a greedy LL parser:

1. no left-recursion
2. no `a+ a` alike sequences
3. longest rule first: rule `<X> ::= a | a b`" must be replaced by `<X> ::= a b | a`
4. special chars `<>(){}[]|+*?:=` each must be quoted with `\`

EBNF syntax:
============

1. terminal symbols must be quoted between `""`
2. rules end with `;`

remaining rules are the same as for BNF syntax.
The tuple example in ebnf becomes:

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

The bnf/ package includes:
==========================

* bnf.py: BNF parser and input sequence scanner
* ebnf.py: extended BNF parser and input sequence scanner

Documentation in the docs/ directory:

* tutorial.html: a complete example
* internals.html: bnf/ebnf routine description

Code generation examples:

* exs/: some demonstration examples

(C) prs, IST 2022
