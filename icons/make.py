#!/usr/bin/env python

import os, wx.tools.img2py

def extractIcon(iconZipFile, pngFilename, pngZipped):
    pngFile = file(pngFilename, 'wb')
    pngFile.write(iconZipFile.read(pngZipped))
    pngFile.close()

def addIcon(pngName, pngFilename, iconPyFile, first):
    options = ['-i', '-c', '-a', '-n%s'%pngName, pngFilename, iconPyFile]
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

def makeSplashScreen(splashPyFile):
    wx.tools.img2py.main(['-c', '-a', '-nsplash', 'splash.png', splashPyFile])

if __name__ == '__main__':
    makeIconPyFile('../taskcoachlib/gui/icons.py')
    makeSplashScreen('../taskcoachlib/gui/icons.py')
