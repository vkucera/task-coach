#!/usr/bin/env python

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

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

import os, wx.tools.img2py

def extractIcon(iconZipFile, pngFilename, pngZipped):
    pngFile = file(pngFilename, 'wb')
    pngFile.write(iconZipFile.read(pngZipped))
    pngFile.close()

def addIcon(pngName, pngFilename, iconPyFile, first):
    # -F: don't generate backwards compatible access functions, since the 
    # generated file isn't backwards compatible anyway (a bug in wxPython
    # 2.8.8.1).
    options = ['-i', '-c', '-a', '-n%s'%pngName, pngFilename, iconPyFile]
    if map(int, wx.__version__.split('.')) >= (2, 8, 8):
        options.insert(0, '-F')
    if first:
        options.remove('-a')
    wx.tools.img2py.main(options)

def extractAndAddIcon(iconZipFile, iconPyFile, pngName, pngZipped, first):
    pngFilename = '%s.png'%pngName
    extractIcon(iconZipFile, pngFilename, pngZipped)
    addIcon(pngName, pngFilename, iconPyFile, first)
    os.remove(pngFilename)

def extractAndAddIcons(iconZipFile, iconPyFile):
    import iconmap
    first = True
    for pngName, pngZipped in iconmap.icons.items(): 
        extractAndAddIcon(iconZipFile, iconPyFile, pngName, pngZipped, first)
        first = False

def makeIconPyFile(iconPyFile):
    if os.path.isfile(iconPyFile):
        os.remove(iconPyFile)

    import zipfile
    iconZipFile = zipfile.ZipFile('nuvola.zip', 'r')
    extractAndAddIcons(iconZipFile, iconPyFile)
    iconZipFile.close()

def makeSplashScreen(iconPyFile):
    options = ['-c', '-a', '-nsplash', 'splash.png', 
               iconPyFile]
    if map(int, wx.__version__.split('.')) >= (2, 8, 8):
        options.insert(0, '-F')
    wx.tools.img2py.main(options)

def fixIconFile(iconFileName):
    ''' wxPython 2.8.8.1 uses a new class for images in the generated image
        file. Since this class is not available in older versions of wxPython 
        we include that file in taskcoachlib.thirdparty and change the import 
        in the generated image file. '''
    fd = file(iconFileName)
    contents = fd.readlines()
    fd.close()
    fd = file(iconFileName, 'w')
    for line in contents:
        if line.startswith('from wx.lib.embeddedimage'):
            line = 'from taskcoachlib.thirdparty.embeddedimage import PyEmbeddedImage\n'
        fd.write(line)
    fd.close()


if __name__ == '__main__':
    iconFileName = '../taskcoachlib/gui/icons.py'
    makeIconPyFile(iconFileName)
    makeSplashScreen(iconFileName)
    fixIconFile(iconFileName)
