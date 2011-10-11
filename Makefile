.PHONY: lint pep8 pyflakes clean

lint: pep8 pyflakes

pep8:
	pep8 --repeat `find wikipedia/ -name \*py`

pyflakes:
	pyflakes import.py
	pyflakes `find wikipedia/ -name \*py`

clean:
	find . -name '*~' -o -name '*.pyc' -print0 | xargs -0 -r rm
	rm env -rf
	rm _trial_temp -rf

check:
	trial wikipedia

build:
	virtualenv --no-site-packages env
	. env/bin/activate
	pip install -r requirements.txt
