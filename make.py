'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>
Copyright (C) 2008 Jerome Laheurte <fraca7@free.fr>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from taskcoachlib import meta
import sys, os, glob
from setup import setupOptions
from buildlib import clean, bdist_rpm_fedora, bdist_deb


setupOptions['cmdclass'] = dict(clean=clean,
                                bdist_rpm_fedora=bdist_rpm_fedora,
                                bdist_deb=bdist_deb)
                                
distdir = 'dist'
builddir = 'build'


manifest = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
    <assemblyIdentity version="0.64.1.0" processorArchitecture="x86" 
    name="Controls" type="win32"/>
    <description>%s</description>
    <dependency>
        <dependentAssembly>
            <assemblyIdentity type="win32" 
            name="Microsoft.Windows.Common-Controls" version="6.0.0.0" 
            processorArchitecture="X86" publicKeyToken="6595b64144ccf1df"
            language="*"/>
        </dependentAssembly>
    </dependency>
</assembly>
"""%meta.name

def writeFile(filename, text, directory='.'):
    if not os.path.exists(directory):
        os.mkdir(directory)
    file = open(os.path.join(directory, filename), 'w')
    file.write(text)
    file.close()

def createDocumentation():
    from taskcoachlib import help
    writeFile('README.txt',  help.aboutText)
    writeFile('INSTALL.txt', help.installText)
    writeFile('LICENSE.txt', meta.licenseText)

def createInnoSetupScript():
    script = file('build.in/windows/taskcoach.iss').read()
    writeFile('taskcoach.iss', script%meta.metaDict, builddir)

def createDebianChangelog():
    changelog = file('build.in/debian/changelog').read()
    writeFile('changelog', changelog%meta.metaDict, 
              os.path.join(builddir, 'debian'))

if sys.argv[1] == 'py2exe':
    from distutils.core import setup
    import py2exe
    py2exeDistdir = '%s-%s-win32exe'%(meta.filename, meta.version)
    setupOptions.update({
        'windows' : [{ 'script' : 'taskcoach.pyw', 
            'other_resources' : [(24, 1, manifest)],
            'icon_resources': [(1, 'icons.in/taskcoach.ico')]}],
        'options' : {'py2exe' : {
            'compressed' : 1, 
            'optimize' : 2, 
            # We need to explicitly include these packages because they 
            # are imported implicitly:
            'packages' : ['taskcoachlib.i18n', 'xml.dom.minidom'], 
            'dist_dir' : os.path.join(builddir, py2exeDistdir),
            'dll_excludes': 'MSVCR80.dll'}},
        'data_files': [('', ['dist.in/gdiplus.dll', 'dist.in/MSVCP71.DLL'])]})
 
elif sys.argv[1] == 'py2app':
    from setuptools import setup
    setupOptions.update(dict(app=['taskcoach.py'], 
        setup_requires=['py2app'],
        options=dict(py2app=dict(argv_emulation=True, compressed=True,
            dist_dir=builddir, optimize=2, iconfile='icons.in/taskcoach.icns', 
            # We need to explicitly include i18n modules because they 
            # are imported implicitly via __import__:
            includes=[filename[:-3].replace('/', '.') for filename \
                      in glob.glob('taskcoachlib/i18n/*.py')],
            plist=dict(CFBundleIconFile='taskcoach.icns')))))
    
elif sys.argv[1] == 'bdist_rpm_fedora':
    from distutils.core import setup
    spec_file = file('build.in/fedora/taskcoach.spec').read()%meta.metaDict
    spec_file = spec_file.split('\n')
    setupOptions.update(dict(options=dict(bdist_rpm_fedora=dict(\
        spec_file=spec_file, icon='icons.in/taskcoach.png', 
        desktop_file='build.in/fedora/taskcoach.desktop'))))
    # On Fedora, to keep the rpm build process going when it finds 
    # unpackaged files you need to create a ~/.rpmmacros file 
    # containing the line '%_unpackaged_files_terminate_build 0'.

elif sys.argv[1] == 'bdist_deb':
    from distutils.core import setup
    setupOptions.update(dict(options=dict(bdist_deb=dict(\
        package=meta.data.filename_lower, title=meta.data.name, 
        description=meta.data.description, 
        long_description=meta.data.long_description, 
        version=meta.data.version,
        author=meta.data.author, author_email=meta.data.author_email,
        copyright=meta.data.copyright,
        license=meta.data.license_title_and_version, 
        license_abbrev=meta.data.license_title_and_version_abbrev,
        license_path='/usr/share/common-licenses/GPL-3',
        license_summary=meta.data.license_notice, 
        wxpythonversion=meta.data.wxpythonversionnumber,
        subsection='Office', url=meta.data.url,
        command='/usr/bin/taskcoach.py'))))
    
else:
    from distutils.core import setup


if __name__ == '__main__':
    for directory in builddir, distdir:
        if not os.path.exists(directory):
            os.mkdir(directory)
    createDocumentation()
    setup(**setupOptions)
    if sys.argv[1] == 'py2exe':
        createInnoSetupScript()
