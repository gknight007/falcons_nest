
package { 'falcon':
  ensure   => latest,
  provider => 'pip',
}

package { [
    'gevent',
    'daemonize',
    'lockfile',
  ]:
  ensure   => latest,
  provider => 'pip',
}



package { [
    'python-nose',
  ]:
  ensure   => latest,
}


