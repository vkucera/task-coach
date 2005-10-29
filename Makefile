# Makefile to create binary and source distributions and generate the 
# simple website (intermediate files are in ./build, the files for the
# website end up in ./dist)


ifeq "$(OSTYPE)" "linux"
    PYTHON="python"
    WEBCHECKER="/usr/share/doc/python2.4/examples/Tools/webchecker/webchecker.py" 
    GETTEXT="pygettext"
else # cygwin:
    PYTHON="python"
    INNOSETUP="/cygdrive/c/Program Files/Inno Setup 5/ISCC.exe"
    WEBCHECKER=i:/Program\ Files/Python24/Tools/webchecker/webchecker.py
    GETTEXT=python i:/Program\ Files/Python24/Tools/i18n/pygettext.py
endif


all: i18n windist sdist website

windist: icons
	$(PYTHON) make.py py2exe
	$(INNOSETUP) build/taskcoach.iss

wininstaller:
	$(INNOSETUP) build/taskcoach.iss

sdist: icons changes
	$(PYTHON) make.py sdist --formats=zip,gztar --no-prune

icons:
	cd icons.in; $(PYTHON) make.py

website: changes
	cd website.in; $(PYTHON) make.py; cd ..
	$(PYTHON) $(WEBCHECKER) dist/index.html

i18n:
	$(GETTEXT) --output-dir i18n.in taskcoachlib
	cd i18n.in; $(PYTHON) make.py

changes:
	$(PYTHON) changes.in/make.py text > CHANGES.txt
	$(PYTHON) changes.in/make.py html > website.in/changes.html
 

CLEANFILES=*.pyc */*.pyc */*/*.pyc dist build MANIFEST README.txt INSTALL.txt LICENSE.txt CHANGES.txt @webchecker.pickle
REALLYCLEANFILES=taskcoachlib/gui/icons.py taskcoachlib/i18n/??_??.py

clean:
	rm -rf $(CLEANFILES)

reallyclean:
	rm -rf $(CLEANFILES) $(REALLYCLEANFILES)

