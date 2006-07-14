# Makefile to create binary and source distributions and generate the 
# simple website (intermediate files are in ./build, distributions are
# put in ./dist, the files for the website end up in ./website.out)

PYTHON="python" # python should be on the path

ifeq ($(shell uname),Linux)
    PYTHONTOOLDIR="/usr/share/doc/python2.4/examples/Tools"
    GETTEXT="pygettext"
endif

ifeq ($(shell uname),Darwin)
    PYTHONTOOLDIR="/Applications/MacPython 2.4/Extras/Tools"
    GETTEXT=python $(PYTHONTOOLDIR)/i18n/pygettext.py
endif

ifeq ($(shell uname),CYGWIN_NT-5.1)
    PYTHONEXE=$(shell python -c "import sys, re; print re.sub('/cygdrive/([a-z])', r'\1:', '\ '.join(sys.argv[1:]))" $(shell which $(PYTHON)))
    PYTHONTOOLDIR=$(dir $(PYTHONEXE))/Tools
    INNOSETUP="/cygdrive/c/Program Files/Inno Setup 5/ISCC.exe"
    GETTEXT=python $(PYTHONTOOLDIR)/i18n/pygettext.py
endif

WEBCHECKER=$(PYTHONTOOLDIR)/webchecker/webchecker.py


all: windist sdist website

windist: icons i18n
	$(PYTHON) make.py py2exe
	$(INNOSETUP) build/taskcoach.iss

wininstaller:
	$(INNOSETUP) build/taskcoach.iss

sdist: icons changes i18n
	$(PYTHON) make.py sdist --formats=zip,gztar --no-prune

macdist: icons i18n
	$(PYTHON) make.py py2app
	hdiutil create -ov -imagekey zlib-level=9 -srcfolder build/TaskCoach.app dist/TaskCoach.dmg

icons:
	cd icons.in; $(PYTHON) make.py

website: changes
	cd website.in; $(PYTHON) make.py; cd ..
	$(PYTHON) $(WEBCHECKER) website.out/index.html

i18n:
	$(GETTEXT) --output-dir i18n.in taskcoachlib
	cd i18n.in; $(PYTHON) make.py

changes:
	$(PYTHON) changes.in/make.py text > CHANGES.txt
	$(PYTHON) changes.in/make.py html > website.in/changes.html
 

CLEANFILES=*.pyc */*.pyc */*/*.pyc build dist website.out MANIFEST README.txt INSTALL.txt LICENSE.txt CHANGES.txt @webchecker.pickle
REALLYCLEANFILES=taskcoachlib/gui/icons.py taskcoachlib/i18n/??_??.py

clean:
	rm -rf $(CLEANFILES)

reallyclean:
	rm -rf $(CLEANFILES) $(REALLYCLEANFILES)

