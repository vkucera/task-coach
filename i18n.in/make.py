import glob, po2dict, shutil

for poFile in glob.glob('*.po'):
    pyFile = po2dict.make(poFile)
    shutil.copyfile(pyFile, '../taskcoachlib/i18n/%s'%pyFile)
