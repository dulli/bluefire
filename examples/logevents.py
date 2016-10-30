""" Example that uses outputs button events from a Amazon Fire TV Remote """
import logging
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))
import plac

from remote import FireRemote
from lib import log

_LOG = logging.getLogger(__name__)
_PID = os.getpid()

_DEVICE_MAC = "54:4A:16:4D:AC:32"
_CONTROLLER_MAC = "00:1A:7D:DA:71:13"
_TIMEOUT = 60

def main(debug: ("Enable debug output", 'flag', 'd'),
         connect: ("Force a new connection", 'flag', 'c')):
    """ Start the example script """
    log.setup('eventlogger.log', debug)
    _LOG.info('EventLogger started with PID %i', _PID)
    _LOG.info('This example will end after it has been idle for %i seconds', _TIMEOUT)

    remote = FireRemote(_DEVICE_MAC if connect else _CONTROLLER_MAC)
    remote.events.listen(lambda k: _LOG.info('Pressed %s', k), 'down')
    remote.events.listen(lambda k: _LOG.info('Released %s', k), 'up')
    try:
        mode = remote.MODE_CONNECT if connect else remote.MODE_LISTEN
        remote.connect(mode, _TIMEOUT)
        remote.event_loop()
    except KeyboardInterrupt:
        print('')
        _LOG.info('EventLogger has been terminated...')
    remote.disconnect()

if __name__ == "__main__":
    try:
        plac.call(main)
    except Exception as exception:
        _LOG.error('Something went wrong...')
        _LOG.exception(exception)
