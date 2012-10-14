# Task Coach - Your friendly task manager
# Copyright (C) 2004-2012 Task Coach developers <developers@taskcoach.org>
# 
# Task Coach is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Task Coach is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Makefile to create binary and source distributions and generate the 
# simple website (intermediate files are in ./build, distributions are
# put in ./dist, the files for the website end up in ./website.out)

DOT="dot"       # dot should be on the path

# Python should be on the path. On 64 bits Mac OS X, use the 32-bits version
# (wx only works in 32 bits mode and the environment/default write trick to
# make it the default does not seem to work on Lion).

ifeq "$(shell uname -sm)" "Darwin x86_64"
    PYTHON="python-32"
else
    PYTHON="python"
endif

ifeq (CYGWIN_NT,$(findstring CYGWIN_NT,$(shell uname)))
    INNOSETUP="/cygdrive/c/Program Files/Inno Setup 5/ISCC.exe"
    PORTABLEAPPSINSTALLER="/cygdrive/c/Program Files/PortableApps.comInstaller/PortableApps.comInstaller.exe"
    EPYDOC=$(PYTHON) $(shell python -c "import os, sys; print \"'\" + os.path.join(os.path.split(sys.executable)[0], 'Scripts', 'epydoc.py') + \"'\"")
else
    EPYDOC="epydoc"
endif

TCVERSION=$(shell python -c "import taskcoachlib.meta.data as data; print data.version")
TCPORTABLE=$(shell python -c "import os; print \"'\" + os.path.join(os.getcwd(), 'build', 'TaskCoachPortable') + \"'\"")

ifeq ($(PGPID)x,x)
PGPID=a3e41706
endif

revision:
	echo "revision='$(TCREV)'" > taskcoachlib/meta/revision.py

prepare: thirdpartymodules icons i18n templates

windists: windist winpenpack portableapps sdist_windows

windist: py2exe
	$(INNOSETUP) build/taskcoach.iss

py2exe: prepare
	$(PYTHON) make.py py2exe

sdist_windows: prepare changes templates dist/TaskCoach-$(TCVERSION).zip

dist/TaskCoach-$(TCVERSION).zip:
	$(PYTHON) make.py sdist --formats=zip --no-prune --template=build.in/windows/MANIFEST.in

sdist_linux: prepare changes templates dist/TaskCoach-$(TCVERSION).tar.gz

sdist_ubuntu: sdist_linux
	# Launchpad does not support one size fits all packages...
	cp dist/TaskCoach-$(TCVERSION).tar.gz dist/taskcoach_$(TCVERSION)-0ubuntu10~lucid.tar.gz
	cp dist/TaskCoach-$(TCVERSION).tar.gz dist/taskcoach_$(TCVERSION)-0ubuntu10~maverick.tar.gz
	cp dist/TaskCoach-$(TCVERSION).tar.gz dist/taskcoach_$(TCVERSION)-0ubuntu11~natty.tar.gz
	cp dist/TaskCoach-$(TCVERSION).tar.gz dist/taskcoach_$(TCVERSION)-0ubuntu11~oneiric.tar.gz
	cp dist/TaskCoach-$(TCVERSION).tar.gz dist/taskcoach_$(TCVERSION)-0ubuntu12~precise.tar.gz

dist/TaskCoach-$(TCVERSION).tar.gz:
	$(PYTHON) make.py sdist --formats=gztar --no-prune --template=build.in/debian/MANIFEST.in

rpm: prepare changes templates
	cp build.in/debian/MANIFEST.in .
	$(PYTHON) make.py bdist_rpm --requires "python2.5,python-wxgtk2.8" --group "Applications/Productivity"
	rm MANIFEST.in

fedora: prepare changes templates
	cp build.in/debian/MANIFEST.in .
	$(PYTHON) make.py bdist_rpm_fedora
	rm MANIFEST.in

opensuse: sdist_linux
	cp build.in/debian/MANIFEST.in .
	$(PYTHON) make.py bdist_rpm_opensuse 
	mv dist/taskcoach-$(TCVERSION)-1.noarch.rpm dist/taskcoach-$(TCVERSION)-1.opensuse.i386.rpm
	mv dist/taskcoach-$(TCVERSION)-1.src.rpm dist/taskcoach-$(TCVERSION)-1.opensuse.src.rpm

deb: sdist_linux
	mv dist/TaskCoach-$(TCVERSION).tar.gz dist/TaskCoach_$(TCVERSION).tar.gz
	LC_ALL=C $(PYTHON) make.py bdist_deb --sdist=dist/TaskCoach_$(TCVERSION).tar.gz
	mv dist/taskcoach_$(TCVERSION)-1_all.deb dist/taskcoach_$(TCVERSION)-1.deb

ubuntu: sdist_ubuntu
	LC_ALL=C $(PYTHON) make.py bdist_ubuntu lucid 10 --sdist=dist/taskcoach_$(TCVERSION)-0ubuntu10~lucid.tar.gz
	mv build build-lucid
	LC_ALL=C $(PYTHON) make.py bdist_ubuntu maverick 10 --sdist=dist/taskcoach_$(TCVERSION)-0ubuntu10~maverick.tar.gz
	mv build build-maverick
	LC_ALL=C $(PYTHON) make.py bdist_ubuntu natty 11 --sdist=dist/taskcoach_$(TCVERSION)-0ubuntu11~natty.tar.gz
	mv build build-natty
	LC_ALL=C $(PYTHON) make.py bdist_ubuntu oneiric 11 --sdist=dist/taskcoach_$(TCVERSION)-0ubuntu11~oneiric.tar.gz
	mv build build-oneiric
	LC_ALL=C $(PYTHON) make.py bdist_ubuntu precise 12 --sdist=dist/taskcoach_$(TCVERSION)-0ubuntu12~precise.tar.gz
	mv build build-precise

ppa-sign: ubuntu
	cd build-lucid; debsign -k0x$(PGPID) taskcoach_$(TCVERSION)-0ubuntu10~lucid-1_source.changes
	cd build-maverick; debsign -k0x$(PGPID) taskcoach_$(TCVERSION)-0ubuntu10~maverick-1_source.changes
	cd build-natty; debsign -k0x$(PGPID) taskcoach_$(TCVERSION)-0ubuntu11~natty-1_source.changes
	cd build-oneiric; debsign -k0x$(PGPID) taskcoach_$(TCVERSION)-0ubuntu11~oneiric-1_source.changes
	cd build-precise; debsign -k0x$(PGPID) taskcoach_$(TCVERSION)-0ubuntu12~precise-1_source.changes

ppa-rel: ppa-sign
	cd build-lucid; dput ppa:taskcoach-developers/release-snapshot taskcoach_$(TCVERSION)-0ubuntu10~lucid-1_source.changes
	cd build-maverick; dput ppa:taskcoach-developers/release-snapshot taskcoach_$(TCVERSION)-0ubuntu10~maverick-1_source.changes
	cd build-natty; dput ppa:taskcoach-developers/release-snapshot taskcoach_$(TCVERSION)-0ubuntu11~natty-1_source.changes
	cd build-oneiric; dput ppa:taskcoach-developers/release-snapshot taskcoach_$(TCVERSION)-0ubuntu11~oneiric-1_source.changes
	cd build-precise; dput ppa:taskcoach-developers/release-snapshot taskcoach_$(TCVERSION)-0ubuntu12~precise-1_source.changes

ppa-relnext: ppa-sign
	cd build-lucid; dput ppa:taskcoach-developers/nextrelease-snapshot taskcoach_$(TCVERSION)-0ubuntu10~lucid-1_source.changes
	cd build-maverick; dput ppa:taskcoach-developers/nextrelease-snapshot taskcoach_$(TCVERSION)-0ubuntu10~maverick-1_source.changes
	cd build-natty; dput ppa:taskcoach-developers/nextrelease-snapshot taskcoach_$(TCVERSION)-0ubuntu11~natty-1_source.changes
	cd build-oneiric; dput ppa:taskcoach-developers/nextrelease-snapshot taskcoach_$(TCVERSION)-0ubuntu11~oneiric-1_source.changes
	cd build-precise; dput ppa:taskcoach-developers/nextrelease-snapshot taskcoach_$(TCVERSION)-0ubuntu12~precise-1_source.changes

ppa-release: ppa-sign
	cd build-lucid; dput ppa:taskcoach-developers/ppa taskcoach_$(TCVERSION)-0ubuntu10~lucid-1_source.changes
	cd build-maverick; dput ppa:taskcoach-developers/ppa taskcoach_$(TCVERSION)-0ubuntu10~maverick-1_source.changes
	cd build-natty; dput ppa:taskcoach-developers/ppa taskcoach_$(TCVERSION)-0ubuntu11~natty-1_source.changes
	cd build-oneiric; dput ppa:taskcoach-developers/ppa taskcoach_$(TCVERSION)-0ubuntu11~oneiric-1_source.changes
	cd build-precise; dput ppa:taskcoach-developers/ppa taskcoach_$(TCVERSION)-0ubuntu12~precise-1_source.changes

app: prepare
	$(PYTHON) make.py py2app
	chmod 644 "build/Task Coach/TaskCoach.app/Contents/Resources/taskcoach.py"

dmg-goodies: app
	mkdir "build/Task Coach/.Resources"
	cp -f dist.in/macos/dmg-background.png "build/Task Coach/.Resources/"
	cp -f dist.in/macos/config "build/Task Coach/.DS_Store"
	ln -s /Applications "build/Task Coach/Applications"

dmgbase:
	hdiutil create -ov -imagekey zlib-level=9 -fs "HFS+" -srcfolder "build/Task Coach" dist/TaskCoach-$(TCVERSION).dmg

dmg: dmg-goodies dmgbase

dmg-signed: dmg-goodies
	codesign -f -s "Developer ID Application" -r='designated => certificate leaf[field.1.2.840.113635.100.6.1.13] and identifier "org.pythonmac.unspecified.TaskCoach"' "build/Task Coach/TaskCoach.app"
	make dmgbase

winpenpack: py2exe 
	$(PYTHON) make.py bdist_winpenpack

portableapps: py2exe
	$(PYTHON) make.py bdist_portableapps
	$(PORTABLEAPPSINSTALLER) $(TCPORTABLE)
	mv build/TaskCoachPortable_$(TCVERSION).paf.exe dist

icons: taskcoachlib/gui/icons.py

templates: taskcoachlib/persistence/xml/templates.py

thirdpartymodules:
	cd thirdparty; tar xzf APScheduler-2.0.3.tar.gz --strip-components=1 -C ../taskcoachlib/thirdparty APScheduler-2.0.3/apscheduler
	cd thirdparty; tar xzf chardet-2.1.1.tar.gz --strip-components=1 -C ../taskcoachlib/thirdparty chardet-2.1.1/chardet
	cd thirdparty; tar xzf python-dateutil-1.5.tar.gz --strip-components=1 -C ../taskcoachlib/thirdparty python-dateutil-1.5/dateutil
	cd thirdparty; tar xzf desktop-0.4.1.tar.gz --strip-components=1 -C ../taskcoachlib/thirdparty desktop-0.4.1/desktop
	cd thirdparty; tar xzf keyring-0.9.2.tar.gz --strip-components=1 -C ../taskcoachlib/thirdparty keyring-0.9.2/keyring
	cd taskcoachlib/thirdparty; patch -p1 < ../../thirdparty/patches/APScheduler.diff

taskcoachlib/gui/icons.py: icons.in/iconmap.py icons.in/nuvola.zip icons.in/splash.png
	cd icons.in; $(PYTHON) make.py

taskcoachlib/persistence/xml/templates.py:
	cd templates.in; $(PYTHON) make.py

website: changes
	cd website.in; $(PYTHON) make.py; cd ..
	$(PYTHON) tools/webchecker.py website.out/index.html

epydoc:
	$(EPYDOC) --parse-only -v --simple-term -o epydoc.out taskcoachlib taskcoach.py

dot:
	$(PYTHON) tools/dot.py taskcoachlib/gui/viewer > doc/viewer.dot
	$(PYTHON) tools/dot.py taskcoachlib/gui/dialog > doc/dialog.dot
	$(DOT) -Tpng -Kdot -O doc/*.dot

i18n: templates taskcoachlib/i18n/nl.py

taskcoachlib/i18n/nl.py: i18n.in/messages.pot $(shell find i18n.in -name '*.po')
	cd i18n.in; $(PYTHON) make.py

i18n.in/messages.pot: $(shell find taskcoachlib -name '*.py' | grep -v i18n)
	$(PYTHON) tools/pygettext.py --output-dir i18n.in taskcoachlib

changes:
	$(PYTHON) changes.in/make.py text > CHANGES.txt
	$(PYTHON) changes.in/make.py debian > changelog_content
	$(PYTHON) changes.in/make.py html 7 > website.in/changes.html
	$(PYTHON) changes.in/make.py html > website.in/all_changes.html

unittests: thirdpartymodules icons templates
	cd tests; $(PYTHON) test.py --unittests

integrationtests: thirdpartymodules icons templates
	cd tests; $(PYTHON) test.py --integrationtests

languagetests: thirdpartymodules icons i18n
	cd tests; $(PYTHON) test.py --languagetests

releasetests: thirdpartymodules icons i18n sdist_linux
	cd tests; $(PYTHON) test.py --releasetests

# FIXME: disttests should depend on either windist, deb, rpm or dmg...
disttests:
	cd tests; $(PYTHON) test.py --disttests

alltests: prepare sdist_linux
	cd tests; $(PYTHON) test.py --alltests

coverage: coverage_run coverage_report

coverage_run:
	cd tests; coverage run --source=../taskcoachlib,unittests test.py

coverage_report:
	cd tests; coverage html -d coverage.out --omit=../taskcoachlib/i18n/po2dict.py,../taskcoachlib/i18n/??.py,../taskcoachlib/i18n/???.py,../taskcoachlib/i18n/??_??.py,../taskcoachlib/thirdparty/*.py,../taskcoachlib/meta/debug.py,test.py

pylint:
	-pylint --rcfile=.pylintrc -f html taskcoachlib > pylint.html

CLEANFILES=build build-* website.out MANIFEST README.txt INSTALL.txt LICENSE.txt CHANGES.txt @webchecker.pickle .profile tests/.coverage tests/coverage.out
REALLYCLEANFILES=dist taskcoachlib/gui/icons.py taskcoachlib/persistence/templates.py \
	taskcoachlib/i18n/??.py taskcoachlib/i18n/???.py taskcoachlib/i18n/??_??.py .\#* */.\#* */*/.\#*

clean:
	$(PYTHON) make.py clean
	rm -rf $(CLEANFILES)

reallyclean:
	$(PYTHON) make.py clean --really-clean
	rm -rf $(CLEANFILES) $(REALLYCLEANFILES)

nuke:
	$(PYTHON) nuke.py
