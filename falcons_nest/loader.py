#!/usr/bin/pyton

from os import path, listdir
from traceback import format_exc
import sys
from falcons_nest import FalconsNestStaticDirHandler




class NoBaseClassFound(Exception): pass
class NoMappedClassFound(Exception): pass

class LoaderBase(object):
    '''
    '''
    def __init__(self, wsgiApp, loaderCfg, staticMappings, staticHandler=FalconsNestStaticDirHandler):
        '''
        '''
        self.handlerInfo = {}
        self.wsgiApp = wsgiApp

        self.importClass = loaderCfg.import_class
        self.prefix = loaderCfg.prefix
        self.scriptPrefix = loaderCfg.script_prefix

        self.staticMappings = staticMappings
        self.staticHandler = staticHandler

        self.loadHandlers()
        self.addHandlers()
        self.addStaticHandlers()

    def loadHandlers():
        raise Exception, "ERROR: LoaderBase requires loadHandlers() be sub-classed"

    def addHandlers(self):
        '''
        Add the handlers based on Config
        '''
        for urlHandlerName, handlerRefDict in self.handlerInfo.iteritems():
            self.wsgiApp.add_route(self.scriptPrefix + urlHandlerName, handlerRefDict['class']() )

    def addStaticHandlers(self):
        '''
        '''
        for uriPath, filePath in self.staticMappings.iteritems():
            routePath = path.join(self.prefix, uriPath )
            if routePath == '/':
                routePath = '/{fileName}'
            else:
                routePath = routePath + '/{fileName}'

            print "Mapping %s to directory %s" % (routePath , filePath) #FIXME

            self.wsgiApp.add_route(routePath , self.staticHandler(filePath) )
            
    def testAppClasses(self):
        '''
        '''
        for moduleName, moduleMappings in self.handlerInfo.iteritems():
            try:
                foo = moduleMappings['class']()
            except Exception, err:
                raise Exception, "ERROR In importing handler '%s' in nest...\n\n%s" % (moduleName, format_exc() )
            del foo
            
                            



class PyPathLoader(LoaderBase):
    '''
    '''
    def __init__(self, wsgiApp, loaderCfg, staticMappings):
        self.baseClassName = loaderCfg.path
        LoaderBase.__init__(self, wsgiApp, loaderCfg, staticMappings)


    def loadHandlers(self):
        '''
        '''
        try:
            baseClassRef = __import__(self.baseClassName)
        except:
            raise NoBaseClassFound, 'Unable to find the python class for the API. Check path in the loader config seection'

        for urlPath, handlerName in baseClassRef.falcons_nest_handler_map.iteritems():
            try:
                module = __import__(handlerName)
            except:
                err='Unable to find mapped class %s for URL %s.  Check %s.falcons_nest_handler_map' % (handlerName, urlPath, self.baseClassName)
                raise NoMappedClassFound, err

            if hasattr(module, self.importClass):
                _class = getattr(module, self.importClass)

            self.handlerInfo[handlerName] = {'module': module, 'class': _class}




class DirPathLoader(LoaderBase):
    '''
    '''
    def __init__(self, wsgiApp, loaderCfg, staticMappings):
        self.dirPath = loaderCfg.path
        LoaderBase.__init__(self, wsgiApp, loaderCfg, staticMappings)

    def loadHandlers(self):
        '''
        Given a directory, import all modules into a name space of 
        a random string and keep track of the original file names minus
        the .py at the end
        '''
        #Set the nest as the first place to look for imports
        sys.path.insert(0, self.dirPath)
        
        for aFile in listdir(self.dirPath):
            #Directory test
            if path.isdir(path.join(self.dirPath, aFile)) or aFile[-3:] != '.py':
                continue
            
            #Try to import it
            noPyModuleName = aFile[:-3]
            
            mappedPathName = self.prefix + noPyModuleName
            
            if mappedPathName in self.staticMappings:
                raise Exception, "ERROR: Module %s conflicts with static mapping %s" % self.staticMappsings[mappedPathName]
            try:
                #FIXME: do check against global and currently imported namespace
                #so we ensure we get the expected objects from the nest directory
                #or else we might get cached references to existing imports or 
                #a builtin object
                rPythonModule = __import__(noPyModuleName)
                if not hasattr(rPythonModule , self.importClass):
                    print("Skipping: %s because it has no API class" % noPyModuleName)
                    continue

                self.handlerInfo[noPyModuleName] = {}
                self.handlerInfo[noPyModuleName]['module'] = rPythonModule
                self.handlerInfo[noPyModuleName]['class'] = getattr(self.handlerInfo[noPyModuleName]['module'], self.importClass)
                print "Mapping URI %s to handler %s" % (mappedPathName, path.join(self.dirPath, aFile) )
            except:
                raise #FIXME:
        
        #Remove the nest for the module search path
        sys.path.pop(0)
            

LOADER_TYPES_FILE = ('dir', 'directory', 'file', 'fs')
LOADER_TYPES_PYTHON = ('py', 'python', 'class', 'code')

def getLoaderByType(_type):
  if _type.lower() in LOADER_TYPES_FILE:
    return DirPathLoader

  if _type.lower() in LOADER_TYPES_PYTHON:
    return PyPathLoader

if __name__ == '__main__':
    pass


