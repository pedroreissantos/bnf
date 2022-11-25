#!/usr/bin/env python3
''' eBNF compiler
 a LL parser with backtracking: no left-recursion, no 'a'+ 'a' alike sequences
	backtracking implies that rules "<X> ::= a | a b"
	must be replaced by "<X> ::= a b | a" (longest fule first)

 Syntax: terminals between "", assign with ::=, rules end at ;
 Operators: group (), optional {} or ?, many *, one-or-more +
 Terminal set between [] (not in set [^...]); i.e. range [a-z] ...

 USAGE: python3 ebnf.py [gram.bnf [input.txt]]
 use environment DEBUG=1 for verbose output, for instance:
 $ echo "input sequence" | DEBUG=1 ./ebnf.py gram.bnf

 INTERACTIVE: python3
 >>> import ebnf
 >>> ebnf.grammar('x::= [a-z]+[0-9]*;')
 >>> ebnf.parse('a0')

 Author: Pedro Reis dos Santos
 Date	: April 28, 2021
'''
__all__ = [ 'grammar', 'dump', 'parse', 'ebnf', 'main' ]

from sys import argv, stdin, stdout, exit
from os import environ
from ast import literal_eval
import re

try:
	from ply import lex
	from ply import yacc
except ImportError:
	exit("ply: package not found.\nuse: pip install ply")

# -------------- SCAN ----------------
reserved = { }
tokens = [ 'NT', 'TERM', 'ASSIGN', 'EOL', 'SET', ]
literals = '{}+*|()[]'
t_ASSIGN = r'::='
def t_NT(tok):
	r"[^:= ';#+*?|(){}\[\]\n]+"
	return tok
def t_TERM(tok):
	r"'([^'\\]|\\.)*'"
	tok.value = literal_eval('"'+tok.value+'"')[1:-1] # replace escape squences
	return tok
def t_COMMENT(tok):
	r'\#.*\n'
	tok.lexer.lineno += 1
	# No return value. Token discarded
def t_newline(tok):
	r'\n'
	tok.lexer.lineno += 1
	# No return value. Token discarded
def t_EOL(tok):
	r';'
	return tok
def t_SET(tok):
	r'\[ \^? ([^\\\]]|\\.)+ \]'
	return tok
# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t\r'
# Error handling rule
def t_error(tok):
	''' lexical error handler '''
	print('line', tok.lineno, ": illegal character '%s'" % tok.value[0])
	tok.lexer.skip(1)

def scan(data): # for debug
	''' print scanned tokens '''
	lexer = lex.lex(debug=True)
	lexer.input(data)
	for tok in lexer:
		print(tok)
# -------------- GRAM ----------------
precedence = [('nonassoc', '*', '+'), ('left', '|')]
gram = {}
start = None
nerr = 0
def p_file_1(_):
	'''file : rules '''
def p_rules_1(_):
	'''rules : rule '''
def p_rules_2(_):
	'''rules : rules rule'''
def p_rules_3(_):
	'''rules : rules EOL'''
def p_rule_1(lst):
	'''rule : NT ASSIGN opt EOL'''
	global start
	if not start:
		start = lst[1]
	if lst[1] == '<start>':
		start = lst[1]
	if lst[1] not in gram:
		gram[lst[1]] = lst[3]
	else:
		gram[lst[1]] = '|', gram[lst[1]], lst[3]
def p_opt_1(lst):
	'''opt : opt '|' seq'''
	lst[0] = ('|', lst[1], lst[3],)
def p_opt_2(lst):
	'''opt : seq '''
	lst[0] = lst[1]
def p_seq_1(lst):
	'''seq : '''
	lst[0] = ()
def p_seq_2(lst):
	'''seq : seq lhs'''
	lst[0] = ('_', lst[1], lst[2]) if lst[1] else lst[2]
def p_lhs_1(lst):
	'''lhs : '(' opt ')' '''
	lst[0] = '(', lst[2]
def p_lhs_2(lst):
	'''lhs : '{' opt '}' '''
	lst[0] = '{', lst[2]
def p_lhs_3(lst):
	'''lhs : lhs '*' '''
	lst[0] = '*', lst[1]
def p_lhs_4(lst):
	'''lhs : lhs '+' '''
	lst[0] = '+', lst[1]
def p_lhs_5(lst):
	'''lhs : TERM '''
	lst[0] = 'TERM', lst[1]
def p_lhs_6(lst):
	'''lhs : NT '''
	lst[0] = 'NT', lst[1]
def p_lhs_7(lst):
	'''lhs : lhs '?' '''
	lst[0] = '{', lst[1]
def p_lhs_8(lst):
	'''lhs : SET '''
	lst[0] = '[', lst[1]
def p_error(lst):
	''' syntax error handler '''
	global nerr
	if lst:
		print('line', lst.lineno, ': syntax error at or before', lst.type, '=', lst.value)
	else:
		print('syntax error at end of file (missing ; ?)')
	nerr += 1

def grammar(data):
	''' parse grammar and start symbol from data '''
	global gram, start, nerr
	gram, start, nerr = {}, None, 0
	yacc.yacc(debuglog=yacc.NullLogger()).parse(data, debug=False, tracking=True, lexer=lex.lex())
	if nerr:
		gram, start = {}, None
	return gram, start

def seq(j):
	''' generate a textual representation of a parsed right hand-side rule '''
	out = ''
	if not j:
		pass
	elif j[0] == 'TERM':
		out += j[1] if j[1] not in '' else '\\'+j[1]
	elif j[0] == 'NT':
		out += j[1]
	elif j[0] == '[':
		out += j[1]
	elif j[0] == '(':
		out += '(' + seq(j[1]) + ')'
	elif j[0] == '{':
		out += '{' + seq(j[1]) + '}'
	elif j[0] == '*':
		out += seq(j[1]) + '*'
	elif j[0] == '+':
		out += seq(j[1]) + '+'
	elif j[0] == '|':
		out += seq(j[1]) + '|' + seq(j[2])
	elif j[0] == '_':
		out += seq(j[1]) + '_' + seq(j[2])
	else:
		print('internal error: unknown: ', j[0])
	return out

def dump(gram_ = None, start_ = None): #debug
	''' generate a textual representation of a parsed grammar '''
	if gram_ is None:
		gram_ = gram
	if start_ is None:
		start_ = start
	out = ''
	if not gram_ or not start_:
		return out
	if '<start>' not in gram_:
		out += '<start> ::= ' + start_ + '\n'
	for nterm in gram_:
		out += nterm + '::= ' + seq(gram_[nterm]) + '\n'
	return out

# -------------- INPUT ----------------
recurs = 0
def parse(data, gram_ = None, nterm = None):
	''' process an input data sequence given a grammar and start non-terminal '''
	if gram_ is None:
		gram_ = gram
	if nterm is None:
		nterm = start
	def fit(j, data):
		global recurs
		if not j:
			if debug:
				print('empty:', data)
		elif j[0] == 'TERM':
			if debug:
				print('term', j[1], ':', data)
			cnt = len(j[1])
			if not data or data[:cnt] != j[1]:
				return False, data
			data = data[cnt:]
			recurs = 0
			if debug > 1:
				print('* MATCHED terminal:', j[1])
		elif j[0] == 'NT':
			if debug:
				print('nt', j[1], ':', data)
			if j[1] not in gram_:
				raise ValueError('non-terminal', j[1], 'not in grammar')
			recurs += 1
			if recurs > recursMAX:
				raise ValueError('unbound recursion', recurs, 'in', j[1])
			res = fit(gram_[j[1]], data)
			if not res[0]:
				return False, data
			data = res[1]
			if debug > 1:
				print('* MATCHED non-terminal:', j[1])
		elif j[0] == '[':
			if debug:
				print('set', j[1], ':', data)
			if not data or not re.match(j[1], data[0]):
				return False, data
			data = data[1:]
			recurs = 0
			if debug > 1:
				print('* MATCHED set:', j[1])
		elif j[0] == '|':
			if debug:
				print('alternative', seq(j[1]), '|', seq(j[2]), ':', data)
			res = fit(j[1], data)
			if not res[0]:
				res = fit(j[2], data)
				if not res[0]:
					return False, data
			data = res[1]
		elif j[0] == '_':
			if debug:
				print('sequence', seq(j[1]), '_', seq(j[2]), ':', data)
			res = fit(j[1], data)
			if not res[0]:
				return False, data
			res = fit(j[2], res[1])
			if not res[0]:
				return False, data
			data = res[1]
			if debug > 1:
				print('* MATCHED sequence:', j[1])
		elif j[0] == '(':
			if debug:
				print('group', seq(j[1]), ':', data)
			res = fit(j[1], data)
			if not res[0]:
				return False, data
			data = res[1]
			if debug > 1:
				print('* MATCHED group:', j[1])
		elif j[0] == '{':
			if debug:
				print('optional', seq(j[1]), ':', data)
			res = fit(j[1], data)
			if res[0]:
				data = res[1]
			if debug > 1:
				print('* MATCHED optional:', j[1])
		elif j[0] == '*':
			if debug:
				print('kleen', seq(j[1]), ':', data)
			while True:
				res = fit(j[1], data)
				if not res[0]:
					break
				data = res[1]
			if debug > 1:
				print('* MATCHED kleen:', j[1])
		elif j[0] == '+':
			if debug:
				print('onemany', seq(j[1]), ':', data)
			res = fit(j[1], data)
			if not res[0]:
				return False, data
			while res[0]:
				data = res[1]
				res = fit(j[1], data)
			if debug > 1:
				print('* MATCHED onemany:', j[1])
		return True, data
	if debug:
		print('input: len =', len(data), 'data =', data)
	if nterm not in gram_:
		return False
	res = fit(gram_[nterm], data)
	if debug:
		print(res)
	if res[0] and not res[1]:
		return True
	return False

recursMAX = 200
debug = 0

# -------------- MAIN ----------------
def ebnf(file, data, deb=False):
	''' load grammar and process input data sequence '''
	global debug, gram, start
	if deb:
		debug = 1
	with open(file, encoding="utf8") as fptr:
		gram, start = grammar(fptr.read())
	if debug:
		print(dump(gram, start))
	return parse(data, gram, start) # True or False
	
def main(args):
	''' main function '''
	if len(args) > 1:
		with open(args[1], encoding="utf8") as fptr:
			data = fptr.read()
	else:
		data = stdin.read()
	grammar(data)
	if debug:
		print('start:', start)
	if debug:
		print('gram:', gram)
	if debug:
		print(dump(gram, start))
	if len(args) > 2:
		with open(args[2], encoding="utf8") as fptr:
			data = fptr.read()
	else:
		if stdin.isatty():
			print('input sequence: end with EOF (^D) or use ^D^D to end with no EOL')
		data = stdin.read()
		if stdin.isatty():
			print()
	ret = parse(data, gram, start) # True or False
	if stdout.isatty():
		print(ret)
	exit(0 if ret else 2)

if __name__ == '__main__':
	if 'DEBUG' in environ:
		debug = int(environ['DEBUG'])
	main(argv)
