

from falcons_nest.config import RunningCfg, serverCfgKeys, ConfigError
from falcons_nest import API
from falcons_nest.loader import getLoaderByType
from gevent.pywsgi import WSGIServer
from daemonize import Daemonize
from lockfile import FileLock
from sys import stderr
import argparse
import logging
import signal


runningConfig, runCfg = None, None
runInForeGround = False
runWsgiApp = None

def parseArgs():
  myParser = argparse.ArgumentParser()
  myParser.add_argument('--config', help='Path to configuration file.(optional)')
  myParser.add_argument('--host', help='IP for WSGI server to listen (optional)')
  myParser.add_argument('--port', help='Port for WSGI to listen (optional)')
  myParser.add_argument('--pidfile', help='Path for pidfile of WSGI daemon(optional)')
  myParser.add_argument('--access_log', help='Path to write WSGI server access logs(optional)')
  myParser.add_argument('--error_log', help='Path to write WSGI server error logs(optional)')
  myParser.add_argument('--max_logs', help='Max number of log files to keep(optional)')
  myParser.add_argument('--max_log_size', help='Max size of logs to keep in MB (optional)')
  myParser.add_argument('--loader', help='The loader type [python|dir] (required)')
  myParser.add_argument('--loader_path', help='The path for the app being loaded (requied)')
  myParser.add_argument('--prefix', help='Prefix for ??? (optional')
  myParser.add_argument('--script_prefix', help='Prefox for ??? (optional)')
  myParser.add_argument('--no_daemon', action='store_true', help="Don't run API in daemon process")

  return myParser.parse_args()

def loadConfig(argsIn):
  userCmdLineInfo = {}
  if not hasattr(argsIn, 'config') and getattr(argsIn, 'config') not in (None, ''):
    raise Exception, 'All I require is a --config sir'

  if getattr(argsIn, 'no_daemon'):
    global runInForeGround
    runInForeGround = True

  ## Command line args and cfg keys for
  ## the WSGI server are the same, so just pull from 
  ## parsed args and add to dict for use with running config
  for cfgKey in serverCfgKeys.keys():
    if hasattr(argsIn, cfgKey):
      userCmdLineInfo[cfgKey] = getattr(argsIn, cfgKey)

  ## Command line args and cfg keys for
  ## the WSGI loader are different, so map them
  loaderKeyMap = {
    'loader': 'type',
    'loader_path': 'path',
    'prefix': 'prefix',
    'script_prefix': 'prefix',
  }

  for cmdLineKey, runCfgKey in loaderKeyMap.iteritems():
    if hasattr(argsIn, cmdLineKey):
      inData = getattr(argsIn, cmdLineKey)
      if inData == None: continue
      userCmdLineInfo[runCfgKey] = inData

  global runningConfig
  global runCfg
  try:
    runCfg = runningConfig = RunningCfg(cfgFilePath=argsIn.config, cmdLineInfo=userCmdLineInfo)
  except ConfigError, err:
    stderr.write("%s\n" % err)


def getLoggerFromConfig():
  maxLogBytes = int(runningConfig.server.max_log_size) * 1024 * 1024
  maxNumLogs  = int(runCfg.server.max_logs)

  logFormatStr =  '[%(asctime)s][%(levelname)s][%(process)s] %(message)s'

  logger = logging.getLogger('app_logger')
  logHandler = logging.handlers.RotatingFileHandler(runCfg.server.error_log, maxBytes=maxLogBytes, backupCount=maxNumLogs)
  logHandler.setFormatter(logging.Formatter(logFormatStr))
  logger.addHandler(logHandler)

  return logger
  
  
def loadApp():
  ## Create a WSGI APP object to load our app into
  myApp = API(logger=getLoggerFromConfig())

  ##Get loader class by type
  theAppLoader = getLoaderByType(runCfg.loader.type)

  ##Init loader with loader configs && API() object
  theAppLoader(myApp, runCfg.loader, runCfg.staticMap)

  return myApp


def runApp():
  global runWsgiApp

  if runWsgiApp == None:
    raise Exception, "No runWsgiApp set!"

  socketInfo = (runningConfig.server.host, int(runningConfig.server.port))
  ourLogger = getLoggerFromConfig()

  class LoggerHack(object):
    def __init__(self, logger):
      self.write = logger.critical

  ourWsgiServer = WSGIServer(socketInfo, runWsgiApp, log=LoggerHack(ourLogger))
  ourWsgiServer.handler_class.log_error = ourLogger.error #FIXME: verify this is still needed

  def handleStopSignal(handleStopSignal):
    ourWsgiServer.stop()


  signal.signal(signal.SIGTERM, handleStopSignal)
  ourWsgiServer.serve_forever()


def startApp(ourWsgiApp):
  global runWsgiApp
  runWsgiApp = ourWsgiApp

  if runInForeGround:
    runApp()
    return

  ourPidfile = runningConfig.server.pidfile

  ourDaemon = Daemonize(app = 'wsgiApp', 
                        pid = ourPidfile,
                        action = runApp,
                        verbose = True)
  ourDaemon.start()

def main():
  loadConfig( parseArgs() )
  startApp( loadApp() )


if __name__ == '__main__':
  main()


