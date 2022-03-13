#!/usr/bin/env python3
# eBNF compiler
# with a greedy LL parser: no left-recursion, no 'a'+ 'a' alike sequences
#	greedy implies that rules "<X> ::= a | a b"
#	must be replaced by "<X> ::= a b | a" (longest fule first)
#
# Syntax: terminals between "", assign with ::=, rules end at ;
# Operators: group (), optional {} or ?, many *, one-or-more +
# Terminal set between [] (not in set [^...]); i.e. range [a-z] ...
#
# USAGE: python3 ebnf.py [gram.bnf [input.txt]]
# use environment DEBUG=1 for verbose output, for instance:
# $ echo "input sequence" | DEBUG=1 ./ebnf.py gram.bnf
#
# Author: Pedro Reis dos Santos
# Date	: April 28, 2021
__all__ = [ 'grammar', 'dump', 'parse', 'ebnf', 'main' ]

try: import ply
except:
	import sys
	sys.exit("ply: package not found.\nuse: pip install ply")

# -------------- SCAN ----------------
import ply.lex as lex
reserved = { }
tokens = [ 'NT', 'TERM', 'ASSIGN', 'EOL', 'SET' ]
literals = '{}+*|()[]'
t_ASSIGN = r'::='
def t_NT(t):
	r"[^:= ';#+*?|(){}\[\]\n]+"
	return t
def t_TERM(t):
	r"'([^'\\]|\\.)*'"
	t.value = eval('"'+t.value+'"')[1:-1] # replace escape squences
	return t
def t_COMMENT(t):
	r'\#.*\n'
	pass # No return value. Token discarded
def t_EOL(t):
	r';'
	t.lexer.lineno += len(t.value)
	return t
def t_SET(t):
	r'\[ \^? ([^\\\]]|\\.)+ \]'
	return t
# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t\r\n'
# Error handling rule
def t_error(t):
	print('line', t.lineno, ": illegal character '%s'" % t.value[0])
	t.lexer.skip(1)

def scan(data): # for debug
	lexer = lex.lex(debug=True)
	lexer.input(data)
	for t in lexer:
		print(t)
# -------------- GRAM ----------------
import ply.yacc as yacc
precedence = [('nonassoc', '*', '+'), ('left', '|')]
gram = {}
start = None
nerr = 0
def p_file_1(p):
	'''file : rules '''
def p_rules_1(p):
	'''rules : rule '''
def p_rules_2(p):
	'''rules : rules rule'''
def p_rules_3(p):
	'''rules : rules EOL'''
def p_rule_1(p):
	'''rule : NT ASSIGN opt EOL'''
	global gram, start
	if not start: start = p[1]
	if p[1] == '<start>': start = p[1]
	if p[1] not in gram: gram[p[1]] = p[3]
	else: gram[p[1]] = '|', gram[p[1]], p[3]
def p_opt_1(p):
	'''opt : opt '|' seq'''
	p[0] = '|', p[1], p[3],
def p_opt_2(p):
	'''opt : seq '''
	p[0] = p[1]
def p_seq_1(p):
	'''seq : '''
	p[0] = ()
def p_seq_2(p):
	'''seq : seq lhs'''
	p[0] = ('_', p[1], p[2]) if p[1] else p[2]
def p_lhs_1(p):
	'''lhs : '(' opt ')' '''
	p[0] = '(', p[2]
def p_lhs_2(p):
	'''lhs : '{' opt '}' '''
	p[0] = '{', p[2]
def p_lhs_3(p):
	'''lhs : lhs '*' '''
	p[0] = '*', p[1]
def p_lhs_4(p):
	'''lhs : lhs '+' '''
	p[0] = '+', p[1]
def p_lhs_5(p):
	'''lhs : TERM '''
	p[0] = 'TERM', p[1]
def p_lhs_6(p):
	'''lhs : NT '''
	p[0] = 'NT', p[1]
def p_lhs_7(p):
	'''lhs : lhs '?' '''
	p[0] = '{', p[1]
def p_lhs_8(p):
	'''lhs : SET '''
	p[0] = '[', p[1]
def p_error(p):
	global nerr
	if p: print('line', p.lineno, ': syntax error at or before', p.type, '=', p.value)
	else: print('syntax error at end of file (missing ; ?)')
	nerr += 1

def grammar(data):
	global gram, start, nerr
	gram, start, nerr = {}, None, 0
	yacc.yacc().parse(data, debug=False, tracking=True, lexer=lex.lex())
	if nerr: gram, start = {}, None
	return gram, start

def seq(j):
	out = ''
	if not j: pass
	elif j[0] == 'TERM': out += j[1] if j[1] not in '' else '\\'+j[1]
	elif j[0] == 'NT': out += j[1]
	elif j[0] == '[': out += j[1]
	elif j[0] == '(': out += '(' + seq(j[1]) + ')'
	elif j[0] == '{': out += '{' + seq(j[1]) + '}'
	elif j[0] == '*': out += seq(j[1]) + '*'
	elif j[0] == '+': out += seq(j[1]) + '+'
	elif j[0] == '|': out += seq(j[1]) + '|' + seq(j[2])
	elif j[0] == '_': out += seq(j[1]) + '_' + seq(j[2])
	else: print('internal error: unknown: ', j[0])
	return out

def dump(gram, start): #debug
	out = ''
	if not gram or not start: return out
	if '<start>' not in gram: out += '<start> ::= ' + start + '\n'
	for nt in gram:
		out += nt + '::= ' + seq(gram[nt]) + '\n'
	return out

# -------------- INPUT ----------------
import re
recurs = 0
def parse(gram, nt, data):
	global debug
	def fit(j, data):
		global recurs
		if not j:
			if debug: print('empty:', data)
		elif j[0] == 'TERM':
			if debug: print('term', j[1], ':', data)
			n = len(j[1])
			if not data or data[:n] != j[1]: return False, data
			data = data[n:]
			recurs = 0
			if debug > 1: print('* MATCHED terminal:', j[1])
		elif j[0] == 'NT':
			if debug: print('nt', j[1], ':', data)
			if j[1] not in gram:
				raise ValueError('non-terminal', j[1], 'not in grammar')
			recurs += 1
			if recurs > recursMAX:
				raise ValueError('unbound recursion', recurs, 'in', j[1])
			res = fit(gram[j[1]], data)
			if not res[0]: return False, data
			data = res[1]
			if debug > 1: print('* MATCHED non-terminal:', j[1])
		elif j[0] == '[':
			if debug: print('set', j[1], ':', data)
			if not data or not re.match(j[1], data[0]):
				return False, data
			data = data[1:]
			recurs = 0
			if debug > 1: print('* MATCHED set:', j[1])
		elif j[0] == '|':
			if debug: print('alternative', seq(j[1]), '|', seq(j[2]), ':', data)
			res = fit(j[1], data)
			if not res[0]:
				res = fit(j[2], data)
				if not res[0]: return False, data
			data = res[1]
		elif j[0] == '_':
			if debug: print('sequence', seq(j[1]), '_', seq(j[2]), ':', data)
			res = fit(j[1], data)
			if not res[0]: return False, data
			res = fit(j[2], res[1])
			if not res[0]: return False, data
			data = res[1]
			if debug > 1: print('* MATCHED sequence:', j[1])
		elif j[0] == '(':
			if debug: print('group', seq(j[1]), ':', data)
			res = fit(j[1], data)
			if not res[0]: return False, data
			data = res[1]
			if debug > 1: print('* MATCHED group:', j[1])
		elif j[0] == '{':
			if debug: print('optional', seq(j[1]), ':', data)
			res = fit(j[1], data)
			if res[0]: data = res[1]
			if debug > 1: print('* MATCHED optional:', j[1])
		elif j[0] == '*':
			if debug: print('kleen', seq(j[1]), ':', data)
			while True:
				res = fit(j[1], data)
				if not res[0]: break
				data = res[1]
			if debug > 1: print('* MATCHED kleen:', j[1])
		elif j[0] == '+':
			if debug: print('onemany', seq(j[1]), ':', data)
			res = fit(j[1], data)
			if not res[0]: return False, data
			while res[0]:
				data = res[1]
				res = fit(j[1], data)
			if debug > 1: print('* MATCHED onemany:', j[1])
		return True, data
	if debug: print('input: len =', len(data), 'data =', data)
	if nt not in gram: return False
	res = fit(gram[nt], data)
	if debug: print(res)
	if res[0] and not res[1]: return True
	return False

recursMAX = 200
debug = 0

# -------------- MAIN ----------------
from sys import argv, stdin, stdout, exit
from os import environ

def ebnf(file, data, deb=False):
	global debug
	if deb: debug = 1
	with open(file) as fp: gram, start = grammar(fp.read())
	if debug: print(dump(gram, start))
	return parse(gram, start, data) # True or False
	
def main(argv):
	if len(argv) > 1:
		with open(argv[1]) as file:
			data = file.read()
	else:
		data = stdin.read()
	grammar(data)
	if debug: print('start:', start)
	if debug: print('gram:', gram)
	if debug: print(dump(gram, start))
	if len(argv) > 2:
		with open(argv[2]) as file:
			data = file.read()
	else:
		if stdin.isatty():
			print('input sequence: end with EOF (^D) or use ^D^D to end with no EOL')
		data = stdin.read()
		if stdin.isatty(): print()
	ret = parse(gram, start, data) # True or False
	if stdout.isatty(): print(ret)
	exit(0 if ret else 2)

if __name__ == '__main__':
	if 'DEBUG' in environ: debug = int(environ['DEBUG'])
	main(argv)
