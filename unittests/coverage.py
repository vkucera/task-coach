'''
Title: function-level coverage analysis for unit tests
Submitter: scott moody 
Last Updated: 2005/02/17
Version no: 1.3
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/366089

Description:

Use this recipe to provide simple function/method coverage analysis
within your unit test suites using the following steps within a unit
test file:

import myModule
import coverage

coverage.ignore=[myModule.myClass1,myModule.function7,...]
coverage.watch(myModule)

class TestMyModule:
    def test_one(self):
    .
    .
    .
    def test_coverage(self):
        assert coverage.uncovered()==[]

where:
'myModule' is the module being tested.
'coverage' is the name given to the module containing this recipe.
'coverage.ignore' is an optional list of functions/methods/classes to be
excluded from the coverage analysis.  
'coverage.watch(module_or_class)' is called for each module and/or class 
to include in the coverage analysis.
'coverage.uncovered()' returns a list of functions/methods that were 
not called over the course of the unit test and that are not covered 
by the ignore list.

Discussion:

Sure I'd like every single line of my code to be covered by my unit test
suites. However, during development, I simply want to know that each
function/method is tested at least once to insure that, at a basic
level, my code is working at any given point-in-time. I use this recipe
to develop such unit test suites.

The 'watch' function can be passed a module or class. If passed a
module, it will automatically traverse the module and add coverage for
functions and class methods defined in the module (including methods of
classes defined within classes). If passed a class, coverage will added
to that class and classes defined within that class. To cover multiple
modules/classes, just call 'watch' multiple times.

The 'uncovered' function returns a list of functions and/or methods that
are being watched but were not called over the course of the unit test
suite. I call this function as part of an assert in the very last unit
test to insure the list is empty. If it is not, I either 1) add a test
to cover the uncovered functions/methods or 2) add one or more of the
uncovered functions/methods to the ignore list if I do not want/need
them to be included in the coverage analysis.

The 'ignore' list makes it easy to exclude specific classes, methods,
and/or functions from the coverage analysis. The ignored
functions/methods are still analyzed, but they are ignored by the
'uncovered' function.

I use this recipe with py.test, which outputs the list returned by the
'uncovered' function in the event that the assert fails. I do this in
conjunction with another py.test feature (which may or may not be unique
to py.test) where py.test will capture and withhold stdout (print
statements) *unless* a unit test fails. I take advantage of this feature
by calling a function that will 'pretty print' the uncovered list
*prior* to the assert. Then, if the assert fails, I can see a formatted
representation of what is not being covered. Here is my version of a
pretty print function:

def prettyPrint():
    hierarchy={}
    for c in covers:
        if not c[0] and not ignored(c[1]):
            fMod,fName=c[1].__module__,c[1].func_name
            try:
                fClass=c[1].im_class.__name__
            except:
                fClass='functions'
            try:
                clsDict=hierarchy[fMod]
            except:
                clsDict=dict()
                hierarchy[fMod]=clsDict
            try:
                fList=clsDict[fClass]
                fList.append(fName)
            except:
                clsDict[fClass]=[fName]
    for m in hierarchy.keys():
        print m
        for c in hierarchy[m].keys():
            print '\t',c
            for f in hierarchy[m][c]:
                print '\t\t',f


Notes:

- As it is implemented, the ignore list must be populated *before* the
  'watch' function is called.
- This recipe does not provide separate analysis of classes defined
  within functions.
- The resulting 'covers' list is a list of two-item lists with the form
  [call_count,function]. You can walk this list and report the number of
  times every covered function was called. I placed the call_count
  before the function so that the list could be easily sorted by
  call_count for reporting purposes.
- The 'watch' function uses __dict__ instead of the dir() funtion
  because, for classes, the dir() function returns the methods defined
  in a given class *and* its base classes. This will, somewhat
  obviously, cause problems.
- I have not tested this recipe in conjunction with custom metaclass
  handlers.

'''
from inspect import isroutine,isclass,getmodule
covers=[]
ignore=[]

def watch(scope):
    for attr in scope.__dict__.keys():
        obj=getattr(scope,attr)
        if isroutine(obj) and getmodule(obj)==getmodule(scope):
            setattr(scope,attr,cover(obj))
        elif isclass(obj):
            watch(obj)

def cover(func):
    co=[0,func]
    covers.append(co)
    def cover_proxy(*args,**kw):
        co[0]+=1
        return func(*args,**kw)
    return cover_proxy

def uncovered():
    return [c[1] for c in covers if not c[0] and not ignored(c[1])]

def ignored(func):
    try:
        return func in ignore or func.im_class in ignore
    except:
        return False

