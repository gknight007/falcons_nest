falconet
========


## What is Falcons Nest?
1. An opinionated REST API framework
1. falcon + Gevent WSGI server + REST helpers + dynamic loader for falcon
1. A simple protoduction framework in python
1. A very simple and quick way to turn Python code into a fast REST API with little effort


## What Falcons Nest is not
1. A MVC framework
1. Apache or Nginx

## Installation
Install from source:
```
$ git clone https://github.com/gknight007/falcons_nest.git
$ cd falcons_nest
$ python setup.py install
```


## Running Examples
Lets assume you checked out the source to /tmp and have already ran the source installation steps.
```
$ cd /tmp/falcons_nest
$ falcons_nest -c examples/falcons_nest.cfg --loader_path ./examples
```


## Configuration
There are 2 "things" to be configured for your applications

1. The application loader, either class path based or file system path based
1. The web service daemon.  Listen host, listen port, etc...

See the config example for a details.  All settings have command line overrides for config file settings.  There are defaults.
