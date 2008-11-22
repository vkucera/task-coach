import os, re, glob, sys

if not os.path.exists('dot.out'):
    os.mkdir('dot.out')

packages = []
modules = []
classdef = re.compile('class ([A-Za-z]+)\(([^)]+)\)', re.MULTILINE)

def stripmodule(classname):
    return classname.split('.')[-1]

print 'digraph G {\nrankdir="LR"'

for filename in glob.glob(os.path.join(sys.argv[1], '*.py')):
    contents = file(filename).read()
    matches = classdef.findall(contents)
    if not matches:
        continue
    module = os.path.basename(filename)[:-len('.py')]
    print 'subgraph cluster%s {'%module
    print 'label=%s'%module
    print ' '.join([classes[0] for classes in matches])
    print '}\n'
    for match in matches:
        class_ = stripmodule(match[0])
        superclasses = re.sub('\s', '', match[1]).split(',')
        for superclass in superclasses:
            if superclass == 'object':
                continue
            print '%s->%s'%(stripmodule(superclass), class_)
    print

print '}'
