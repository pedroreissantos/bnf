#!/usr/bin/env python
"""A BNF (Backus-Naur Form) parser and a greedy LL  input sequence scanner
"""

import setuptools

with open("README.md", "r") as fh:
	readme = fh.read()

setuptools.setup(name='bnf', # 'bnf-pkg-peresan',
	version='1.0.1',
	author='Pedro Reis dos Santos',
	author_email="reis.santos@tecnico.ulisboa.pt",
	description="A BNF (Backus-Naur Form) parser and a greedy LL input sequence scanner",
	long_description=readme,
	license = 'MIT',
	url="https://github.com/pedroreissantos/bnf",
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		'Intended Audience :: Developers',
		'Topic :: Software Development :: Compilers',
		'Development Status :: 4 - Beta',
		'Environment :: Console',
	],
	python_requires='>=3.6',
	install_requires=[ 'ply', ],
	py_modules = ['bnf','ebnf'],
	packages=setuptools.find_packages(),
)
