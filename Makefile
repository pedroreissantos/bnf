PKG=bnf-pkg-peresan
ENV=test
REP=testpypi
all::
	python3 setup.py sdist bdist_wheel
install::
	python3 -m twine upload --repository $(REP) dist/*
test::
	python3 -m venv $(ENV)
	source $(ENV)/bin/activate
	pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple $(PKG)
	echo "import package, test and exit"
	python3
clean::
	rm -rf __pycache__ *.egg-info/ dist build $(ENV)
lixo::
	bash -c "python3 -m venv $(ENV); source $(ENV)/bin/activate; pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple $(PKG); echo "import package, test and exit"; python3"
