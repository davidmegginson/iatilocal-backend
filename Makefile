ACTIVATE=./venv/bin/activate

demo: venv
	. $(ACTIVATE) && python -m iatilocal.iatireader

venv: requirements.txt
	rm -rf venv
	python3 -m venv venv
	. $(ACTIVATE) && pip install -r requirements.txt
