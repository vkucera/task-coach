# Makefile to create binary and source distributions and generate the 
# simple website (intermediate files are in ./build, the files for the
# website end up in ./dist)

PYTHON="/cygdrive/c/Program Files/Python24/python.exe"
INNOSETUP="/cygdrive/c/Program Files/Inno Setup 4/ISCC.exe"

all: windist sdist web

windist: theicons
	$(PYTHON) make.py py2exe
	$(INNOSETUP) build/taskcoach.iss

sdist: theicons
	$(PYTHON) make.py sdist --formats=zip,gztar --no-prune

theicons:
	cd icons; $(PYTHON) make.py

web: 
	cd website; $(PYTHON) make.py; cd ..
	$(PYTHON) c:/Program\ Files/Python24/Tools/webchecker/webchecker.py dist/index.html

i18n:
	$(PYTHON) c:/Program\ Files/Python24/Tools/i18n/pygettext.py --output-dir i18n.in taskcoachlib

clean:
	rm -rf *.pyc */*.pyc */*/*.pyc dist build MANIFEST README.txt INSTALL.txt LICENSE.txt messages.pot

