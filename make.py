#!/usr/bin/env python

from distutils.core import setup
from taskcoachlib import meta
import sys, os, glob
from setup import setupOptions
import taskcoach # to add taskcoachlib to the searchpath


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

script = r"""
; Inno Setup Script

[Setup]
AppName=%(name)s
AppVerName=%(name)s %(version)s
AppPublisher=%(author)s
AppPublisherURL=%(url)s
AppSupportURL=%(url)s
AppUpdatesURL=%(url)s
DefaultDirName={pf}\%(filename)s
DefaultGroupName=%(name)s
AllowNoIcons=yes
LicenseFile=../LICENSE.txt
Compression=lzma
SolidCompression=yes
OutputDir=../dist
OutputBaseFilename=%(filename)s-%(version)s-win32 

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "%(filename)s-%(version)s-win32exe\%(filename)s.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "%(filename)s-%(version)s-win32exe\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[INI]
Filename: "{app}\%(filename)s.url"; Section: "InternetShortcut"; Key: "URL"; String: "%(url)s"

[Icons]
Name: "{group}\%(name)s"; Filename: "{app}\%(filename)s.exe"; WorkingDir: "{app}"
Name: "{group}\{cm:ProgramOnTheWeb,%(name)s}"; Filename: "{app}\%(filename)s.url"
Name: "{group}\{cm:UninstallProgram,%(name)s}"; Filename: "{uninstallexe}"
Name: "{userdesktop}\%(name)s"; Filename: "{app}\%(filename)s.exe"; Tasks: desktopicon; WorkingDir: "{app}"
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\%(name)s"; Filename: "{app}\%(filename)s.exe"; Tasks: quicklaunchicon; WorkingDir: "{app}"

[Run]
Filename: "{app}\%(filename)s.exe"; Description: "{cm:LaunchProgram,%(name)s}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\%(filename)s.url"
"""

def writeFile(filename, text, directory=''):
    file = open(os.path.join(directory, filename), 'w')
    file.write(text)
    file.close()

def createDocumentation():
    writeFile('README.txt',  meta.aboutText)
    writeFile('INSTALL.txt', meta.installText)
    writeFile('LICENSE.txt', meta.licenseText)

def createInnoSetupScript():
    writeFile('taskcoach.iss', script%meta.metaDict, builddir)

if sys.argv[1] == 'py2exe':
    import py2exe
    py2exeDistdir = '%s-%s-win32exe'%(meta.filename, meta.version)
    setupOptions.update({
        'windows' : [{ 'script' : 'taskcoach.pyw', 
            'other_resources' : [(24, 1, manifest)],
            'icon_resources': [(1, 'icons/taskcoach.ico')]}],
        'options' : {'py2exe' : {
            'compressed' : 1, 
            'includes' : ['xml.dom.minidom'],
            'optimize' : 2, 
            'dist_dir' : os.path.join(builddir, py2exeDistdir)}}})
 

if __name__ == '__main__':
    if not os.path.exists(builddir):
        os.mkdir(builddir)
    createDocumentation()
    setup(**setupOptions)
    if sys.argv[1] == 'py2exe':
        createInnoSetupScript()
