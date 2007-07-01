# Makefile to create binary and source distributions and generate the 
# simple website (intermediate files are in ./build, distributions are
# put in ./dist, the files for the website end up in ./website.out)

PYTHON="python" # python should be on the path

ifeq ($(shell uname),CYGWIN_NT-5.1)
    INNOSETUP="/cygdrive/c/Program Files/Inno Setup 5/ISCC.exe"
endif

TCVERSION=$(shell python -c "import taskcoachlib.meta.data as data; print data.version")

all: windist sdist website

windist: icons i18n
	$(PYTHON) make.py py2exe
	$(INNOSETUP) build/taskcoach.iss

sdist: icons changes i18n
	$(PYTHON) make.py sdist --formats=zip,gztar --no-prune

rpm: icons changes i18n
	$(PYTHON) make.py bdist_rpm --requires "python>=2.5,python-wxgtk>=2.8.4,python-wxaddons" --group "Applications/Productivity"

deb: rpm
	export EMAIL="frank@niessink.com"
	cd dist; sudo alien --keep-version *.noarch.rpm; cd ..

dmg: icons i18n
	$(PYTHON) make.py py2app
	hdiutil create -ov -imagekey zlib-level=9 -srcfolder build/TaskCoach.app dist/TaskCoach-$(TCVERSION).dmg

icons:
	cd icons.in; $(PYTHON) make.py

website: changes
	cd website.in; $(PYTHON) make.py; cd ..
	$(PYTHON) tools/webchecker.py website.out/index.html

i18n:
	$(PYTHON) tools/pygettext.py --output-dir i18n.in taskcoachlib
	cd i18n.in; $(PYTHON) make.py

changes:
	$(PYTHON) changes.in/make.py text > CHANGES.txt
	$(PYTHON) changes.in/make.py html > website.in/changes.html
 
unittests:
	cd tests; $(PYTHON) test.py

alltests:
	cd tests; $(PYTHON) test.py --alltests

releasetests:
	cd tests; $(PYTHON) test.py --releasetests --no-unittests

integrationtests:
	cd tests; $(PYTHON) test.py --integrationtests --no-unittests
    

CLEANFILES=*.pyc */*.pyc */*/*.pyc */*/*/*.pyc build dist website.out MANIFEST README.txt INSTALL.txt LICENSE.txt CHANGES.txt @webchecker.pickle .profile
REALLYCLEANFILES=taskcoachlib/gui/icons.py taskcoachlib/i18n/??_??.py *.bak */*.bak */*/*.bak .\#* */.\#* */*/.\#*

clean:
	rm -rf $(CLEANFILES)

reallyclean:
	rm -rf $(CLEANFILES) $(REALLYCLEANFILES)

