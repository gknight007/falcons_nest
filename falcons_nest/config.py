#!/usr/bin/python

from os import path, stat
from ConfigParser import ConfigParser
from json import dumps
from falcons_nest.loader import LOADER_TYPES_PYTHON, LOADER_TYPES_FILE
from stat import S_IWUSR, S_IWGRP, S_IWOTH
from socket import gethostbyname_ex

### 
### 
### CONFIGURATION section.  We load 2 types of configs....
### server configs (for the WSGI server) and loader configs 
### (this tells us which code to load into the API and serve)
###
###


### Default values and config keys
### for the WSGI server
serverCfgKeys = {
  'host': 'localhost',
  'port': '8080',
  'pidfile': '/tmp/falcons_nest.pid',
  'access_log': '/tmp/falcons_nest.access.log',
  'error_log': '/tmp/falcons_nests.error.log',
  'max_logs': '1',
  'max_log_size': '300',
  
}



### Default values and config keys
### needed for loading
loaderCfgKeys = {
  'type': None,
  'path': None,
  'prefix': '/',
  'script_prefix': '/',
  'import_class': 'APP',
}


### Key mappings for our 2 config types
cfgFileMap = {
  'server': serverCfgKeys,
  'loader': loaderCfgKeys,
}


def getAllConfigKeys():
  '''
  Returns a list of all config keys available.
  Intended for use with command line argument parsing
  '''
  ret = []
  for cfgType, cfgDefaults in cfgFileMap.iteritems():
    ret.extend( cfgDefaults.keys() )

  return ret

### An empty object we can build
### up later with config data
### using setattr
class AnonObj(object):pass
class ConfigError(object): pass


class RunningCfg(object):
  '''
  '''
  def __init__(self, cfgFilePath=None, cmdLineInfo={}):
    ### Create places for server and loader configs
    self.server = AnonObj()
    self.loader = AnonObj()


    ### Save space for static file mapping too!
    self.staticMap = {}

    self.cfgFilePath = cfgFilePath
    self.cmdLineInfo = cmdLineInfo

    self.loadDefaults()
    self.loadCfgFromFile()
    self.loadCmdLineOpts()
    self.checkErrors()


  def loadDefaults(self):
    ## Iterate over both server and loader config sectoins as topAttr variable
    for cfgSection in cfgFileMap.keys(): 
      topAttr = getattr(self, cfgSection)
      ## Based on the dictionary mappings above, set default config values
      for keyName, defaultValue in cfgFileMap[cfgSection].iteritems():
        if defaultValue == None:
          continue
        setattr(topAttr, keyName, defaultValue)


  def loadCfgFromFile(self):
    if not self.cfgFilePath or not path.exists(self.cfgFilePath):
      return

    cfg = ConfigParser()
    cfg.read(self.cfgFilePath)

    ## Iterate over both server and loader config sectoins as topAttr variable
    for cfgSection in cfgFileMap.keys(): 
      if not cfg.has_section(cfgSection):
        continue #FIXME: might want to raise error here... or warn

      ## This is now either self.server or self.loader depending on which key we are on
      topAttr = getattr(self, cfgSection)

      ## Let check the config file for a matchint config entry
      ## if we find it, set it and override any previous value
      for keyName in cfgFileMap[cfgSection].keys():
        if cfg.has_option(cfgSection, keyName):
          setattr(topAttr, keyName, cfg.get(cfgSection, keyName))
        else:
          print "Missing %s in section %s" % (keyName, cfgSection)
      

    ### Allow for static mapping of files to be configured
    if cfg.has_section('static_map'):
      for uriPath, dirPath in cfg.items('static_map'):
        self.staticMap[uriPath] = dirPath


  def loadCmdLineOpts(self):
    for cmdLineKey, cmdLineValue in self.cmdLineInfo.iteritems():
      if cmdLineValue == None:
        continue

      for cfgSection in cfgFileMap.keys():
        if cmdLineKey in cfgFileMap[cfgSection]:
          topAttr = getattr(self, cfgSection)
          setattr(topAttr, cmdLineKey, cmdLineValue)

  def canWritePath(self, aPath):
    pathMode = stat(aPath).st_mode

    userWrite  = bool( pathMode & S_IWUSR )
    grpWrite   = bool( pathMode & S_IWGRP )
    otherWrite = bool( pathMode & S_IWOTH )

    return userWrite or grpWrite or otherWrite
    
  def checkErrors(self):
    # loader type given
    if not hasattr(self.loader, 'type'):
      raise ConfigError, 'ERROR: No loader type specified.'

    ourLoader = self.loader.type
    if ourLoader not in LOADER_TYPES_FILE and ourLoader not in LOADER_TYPES_PYTHON:
      raise ConfigError, 'ERROR: Invalid loader type %s' % ourLoader

    # loaeder path valid and exists
    if not self.loader.path:
      raise ConfigError, 'ERROR: You did not specifiy a loader path!'

    if self.loader.path in LOADER_TYPES_FILE:
      if not path.isdir(self.loader.path):
        raise ConfigError, 'ERROR: File loader path is not a directory: %s' % self.loader.path

    #Loading errors for python classes will be handled at load time

    # valid host type given
    try:
      gethostbyname_ex(self.server.host)
    except:
      raise ConfigError, 'ERROR: Invalid server.host %s' % self.server.host

    # port given is int and available for bind
    try:
      portAsInt = int(self.server.port)
    except:
      raise ConfigError, 'ERROR: server.port is not an integer'

    if portAsInt > 65536 or portAsInt < 0:
      raise ConfigError, 'ERROR: server.port is an invalid TCP port number'

    # we can write to dir for pid file and log files
    needWrite = {
      'pidfile': self.server.pidfile,
      'access_log': self.server.access_log,
      'error_log': self.server.error_log
    }

    for description, ourFile in needWrite.iteritems():
      if path.exists(ourFile) and not self.canWritePath(ourFile):
          raise ConfigError, "ERROR: Unable to write to %s at '%s'" % (description, ourFile)
      else:
        accessLogDir = path.dirname(ourFile)
        if not path.exists(accessLogDir):
          raise ConfigError, "ERROR: %s directory, %s, doesn't exist!" % (description, accessLogDir)

        elif not self.canWritePath(accessLogDir):
          raise ConfigError, 'ERROR: %s directory, %s no write perms' % (description, accessLogDir)
    # max log size and # logs are positive ints
    posInt = {'max_logs': self.server.max_logs, 'max_log_size': self.server.max_log_size}
    for description, cfgSetting in posInt.iteritems():
      try:
        intCfgSetting = int(cfgSetting)
      except:
        raise ConfigError, 'ERROR: %s must be a number' % description

    if 0 > intCfgSetting:
      raise ConfigError, 'ERROR: %s must be a positive number' % description
    



