""" Example that uses the Kodi EventClient to relay button presses from a Fire TV
    Remote to Kodi """
import logging
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))
import plac

from bluefire import FireRemote
from lib import log
from lib.kodievc import SimpleEventClient

_LOG = logging.getLogger(__name__)
_PID = os.getpid()

_DEVICE_MAC = "54:4A:16:4D:AC:32"
_CONTROLLER_MAC = "00:1A:7D:DA:71:13"

class EventClient(object):
    """ EventClient implementation with a keymap for the Fire TV Remote """
    keymap = {
        'KEY_KPENTER' : 'enter', #0x10F,
        'KEY_BACK' : 'browser_back', #0xa6,
        'KEY_MENU' : 'menu', #0x13f,
        'KEY_LEFT' : 'left', #0x114,
        'KEY_UP' : 'up', #0x111,
        'KEY_RIGHT' : 'right', #0x113,
        'KEY_DOWN' : 'down', #0x112,
        'KEY_REWIND' :'rewind', #0xBA,
        'KEY_FASTFORWARD' : 'fastforward', #0xBB,
        'KEY_PLAYPAUSE' : 'play_pause', #0xB3,
        'KEY_HOMEPAGE' : 'browser_home', #0xAC,
        'KEY_SEARCH' : 'browser_search' #0xAA,
    }

    def __init__(self, name, host, port=9777):
        self.name = name
        self.evc = SimpleEventClient(host, port)

    def press(self, code):
        """ Send a key press event to Kodi """
        self.evc.send_button(self.keymap[code], 'down')

    def release(self, code):
        """ Send a key release event to Kodi """
        self.evc.send_button(self.keymap[code], 'up')

def main(ip_address: ("Host that runs Kodi"),
         debug: ("Enable debug output", 'flag', 'd'),
         connect: ("Force a new connection", 'flag', 'c'),
         timeout: ("Idle duration after which the remote disconnects", 'option', 't', int)=300):
    """ Start the example script """
    log.setup('kodi.log', debug)
    _LOG.info('Kodi remote proxy started with PID %i', _PID)

    reconnect = True
    remote = FireRemote(_DEVICE_MAC if connect else _CONTROLLER_MAC)
    evc = EventClient("Fire TV Remote", ip_address)
    remote.events.listen(evc.press, 'down')
    remote.events.listen(evc.release, 'up')
    while reconnect:
        try:
            mode = remote.MODE_CONNECT if connect else remote.MODE_LISTEN
            remote.connect(mode, timeout)
            remote.event_loop()
        except KeyboardInterrupt:
            print('')
            reconnect = False
            _LOG.info('Kodi remote proxy has been terminated...')
    remote.disconnect()

if __name__ == "__main__":
    try:
        plac.call(main)
    except Exception as exception:
        _LOG.error('Something went wrong...')
        _LOG.exception(exception)
