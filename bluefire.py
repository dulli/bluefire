""" Python 3 Bluetooth HID Input Implementation """
import logging
import socket

_LOG = logging.getLogger(__name__)

class _HID(object):
    _BUFFER_SIZE = 1024
    _L2CAP_MTU = 64
    _RECV_TIMEOUT = 10
    _BACKLOG = 1
    _DATA = 0xA0
    _TYPE_INPUT = 0x01

    MODE_LISTEN = 'listen'
    MODE_CONNECT = 'connect'

    def __init__(self, addr):
        self.addr = addr
        self.idle = 0
        self.connected = False
        self.control = None
        self.interrupt = None
        self.timeout = 100
        self._channels = {}

    def open_channel(self, psm, mode, protocol=socket.BTPROTO_L2CAP):
        """ Open a socket on the given PSM that either listens for incoming
            connections or connects to a remote device directly """
        bluetooth_socket = socket.socket(socket.AF_BLUETOOTH,
                                         socket.SOCK_STREAM,
                                         protocol)
        #bluetooth_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        if mode == HIDDevice.MODE_CONNECT:
            bluetooth_socket.connect((self.addr, psm))
            self.connected = True
        elif mode == HIDDevice.MODE_LISTEN:
            bluetooth_socket.bind((self.addr, psm))
            #bluetooth.set_l2cap_mtu(bluetooth_socket, self._L2CAP_MTU)
            bluetooth_socket.settimeout(self._RECV_TIMEOUT)
            bluetooth_socket.listen(self._BACKLOG)
        self._channels[psm] = bluetooth_socket
        return psm

    def _accept_connection(self, channel):
        channel, addr = channel.accept()
        channel.settimeout(self._RECV_TIMEOUT)
        _LOG.debug('Accepted %s', addr)
        return channel

    def _wait_for_connection(self):
        accepted = []
        connected = False
        while not connected:
            try:
                for psm in self._channels:
                    if psm not in accepted:
                        self._channels[psm] = self._accept_connection(self._channels[psm])
                        accepted.append(psm)
                connected = True
            except socket.timeout: #bluetooth.btcommon.BluetoothError:
                connected = False
        return connected

    def connect(self, mode, interrupt, control, timeout):
        """ Open the interrupt and control channels on the given PSMs """
        _LOG.debug("Control PSM: %i, Interrupt PSM: %i", control, interrupt)
        self.idle = 0
        self.control = self.open_channel(control, mode)
        self.interrupt = self.open_channel(interrupt, mode)
        self.timeout = timeout
        if mode == _HID.MODE_LISTEN:
            _LOG.info('Waiting for Bluetooth connection...')
            self.connected = self._wait_for_connection()


    def disconnect(self):
        """ Close the open and control channels """
        self.connected = False
        for psm in self._channels:
            try:
                self._channels[psm].shutdown(socket.SHUT_RDWR)
            except ConnectionResetError:
                _LOG.warning('Socket has already been shut down...')
            self._channels[psm].close()
        self._channels = {}

    def _parse_message(self, msg):
        hdr = (msg[0] & 0xF0, msg[0] & 0x0F)
        if hdr == (self._DATA, self._TYPE_INPUT):
            data = (msg[1] << 16) + (msg[2] << 8) + msg[3]
            return (hdr, data)
        else:
            _LOG.debug('Ignoring message with unsupported type: %s', msg)
            return (hdr, None)

    def listen(self, callback):
        """ Listen for activity on the interrupt channel """
        while self.connected:
            try:
                message = self._channels[self.interrupt].recv(self._BUFFER_SIZE)
                if message:
                    self.idle = 0
                    _, data = self._parse_message(message)
                    if data is not None:
                        callback(data)
            except socket.timeout: #bluetooth.btcommon.BluetoothError:
                self.idle += self._RECV_TIMEOUT
                if self.idle > self.timeout:
                    self.disconnect()
                    _LOG.info('HID device has been idle for %is...', self.timeout)
                    break
            except TimeoutError:
            except ConnectionResetError:
                _LOG.warning('Connection has been reset by peer, disconnecting...')
                self.disconnect()
                break

class HIDEvents(object):
    """ Trigger callbacks that are registered to key press/release events """
    def __init__(self):
        self.current = []
        self.previous = []
        self._listeners = {'down':[], 'up':[]}

    def _fire_down(self, keycode):
        _LOG.debug('Pressed:\t%s', keycode)
        for callback in self._listeners['down']:
            callback(keycode)

    def _fire_up(self, keycode):
        _LOG.debug('Released:\t%s', keycode)
        for callback in self._listeners['up']:
            callback(keycode)

    def fire(self, keys):
        """ Compare the provided list of currently pressed keys to a list of keys
            that were previously held down and fire the events for any changes """
        self.previous = self.current
        self.current = keys
        for key in self.current + self.previous:
            if key not in self.previous:
                self._fire_down(key)
            if key not in self.current:
                self._fire_up(key)

    def listen(self, callback, direction):
        """ Register a new callback function for the given event """
        _LOG.debug('Added callback: %s (%s)', callback.__name__, direction)
        self._listeners[direction].append(callback)

class HIDDevice(object):
    """ Boilerplate for any HID device """
    MODE_LISTEN = _HID.MODE_LISTEN
    MODE_CONNECT = _HID.MODE_CONNECT

    CONTROL_PSM = 0x0011
    INTERRUPT_PSM = 0x0013

    def __init__(self, addr):
        self.bluetooth_hid = _HID(addr)
        self.events = HIDEvents()

    def connect(self, mode, timeout, interrupt=INTERRUPT_PSM, control=CONTROL_PSM):
        """ Connect to the device on the given interrupt and control channels """
        self.bluetooth_hid.connect(mode, interrupt, control, timeout)
        _LOG.info('Connected to Bluetooth HID device')

    def disconnect(self):
        """ Disconnect from the device """
        self.bluetooth_hid.disconnect()

class FireRemote(HIDDevice):
    """ HID implementation for the Amazon Fire TV Remote """
    _keys = [
        ("KEY_SEARCH", 0x000001),
        ("KEY_UP", 0x000200),
        ("KEY_HOMEPAGE", 0x002000),
        ("KEY_BACK", 0x200000),
        ("KEY_RIGHT", 0x000400),
        ("KEY_DOWN", 0x004000),
        ("KEY_LEFT", 0x040000),
        ("KEY_KPENTER", 0x400000),
        ("KEY_FASTFORWARD", 0x000800),
        ("KEY_MENU", 0x008000),
        ("KEY_REWIND", 0x080000),
        ("KEY_PLAYPAUSE", 0x800000)
    ]

    def _get_keys(self, data):
        for keyname, keymask in self._keys:
            if data & keymask == keymask:
                yield keyname

    def _handle_report(self, input_report):
        keys = [key for key in self._get_keys(input_report)]
        self.events.fire(keys)

    def event_loop(self):
        """ Listen for button events """
        _LOG.info('Listening for button events...')
        self.bluetooth_hid.listen(self._handle_report)
