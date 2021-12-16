""" Minimalistic implementation of Kodis's UDP based EventServer input system.
    Omits PING and BYE packets as those don't seem to be necessary anyway (HELO
    packets are available even though they don't need to be used either) """

from struct import pack
from socket import socket, AF_INET, SOCK_DGRAM
from time import time

class SimpleEventClient(object):
    """ EventClient that can announce new connections to Kodi and send UP and
        DOWN button events using the button name, this assumes that all buttons
        are in the KB keymap. """
    _SIGNATURE = b"XBMC"
    _VERSION = pack("!H", 0x200)
    _SEQ = pack("!I", 0x01)
    _MAXSEQ = pack("!I", 0x01)
    _TOKEN = pack("!I", (int)(time()) & 0xFFFFFFFF)
    _RESERVED_HDR = b"\0" * 10

    _TYPE_HELO = pack("!H", 0x01)
    _ICON = b"\0"
    _RESERVED_PORT = pack("!H", 0x00)
    _RESERVED_HELO = pack("!I", 0x00) + pack("!I", 0x00)

    _TYPE_BUTTON = pack("!H", 0x03)
    _FLAG_DOWN = pack("!H", 0x4b)
    _FLAG_UP = pack("!H", 0x4d)
    _CODE = pack("!H", 0x00)
    _RAW_FLAG_DOWN = pack("!H", 0x0a)
    _RAW_FLAG_UP = pack("!H", 0x0c)
    _AMOUNT = pack("!H", 0x00)
    _KEYMAP = b"KB\0"

    def __init__(self, ip, port):
        self._sock = socket(AF_INET, SOCK_DGRAM)
        self._addr = (ip, port)

    def _send_message(self, packet_type, payload):
        payload_size = pack('!H', len(payload))
        message = self._get_header(packet_type, payload_size)+payload
        return self._sock.sendto(message, self._addr)

    def _get_header(self, packet_type, payload_size):
        header = self._SIGNATURE+self._VERSION+packet_type+self._SEQ+self._MAXSEQ
        header += payload_size+self._TOKEN+self._RESERVED_HDR
        return header

    def send_helo(self, name):
        """ Announce a new client to Kodi """
        name = bytes(name[0:128]+'\0', 'utf-8')
        payload = name+self._ICON+self._RESERVED_PORT+self._RESERVED_HELO
        return self._send_message(self._TYPE_HELO, payload)

    def send_raw_button(self, code, direction):
        """ Send a button event (either 'up' or 'down') """
        code = pack("!H", code)
        flag = self._RAW_FLAG_UP if direction is 'up' else self._RAW_FLAG_DOWN
        payload = code+flag+self._AMOUNT+b"\0\0"
        return self._send_message(self._TYPE_BUTTON, payload)

    def send_button(self, name, direction):
        """ Send a button event (either 'up' or 'down') """
        name = bytes(name+'\0', 'utf-8')
        flag = self._FLAG_UP if direction is 'up' else self._FLAG_DOWN
        payload = self._CODE+flag+self._AMOUNT+self._KEYMAP+name
        return self._send_message(self._TYPE_BUTTON, payload)
