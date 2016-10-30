# BlueFire: A minimal (= incomplete) Python 3 Bluetooth HID Input Implementation
In its core, __BlueFire__ provides Python 3 support for the bluetooth Amazon Fire
TV remote control as a simple input device. As this is however based on a reqular
implementation of the _Bluetooth HID_ protocol (that is also used by other
bluetooth input devices like keyboards and game controllers) it should be easily
possible to support most other bluetooth input devices.

## Setup
While this code should be portable to any system and python version that provides
native bluetooth sockets, it has only been tested on Raspberry PI 1Bs running
_Raspbian Wheezy/Jessie_ with _Python 3.4/3.5_ so far.

### Raspbian/BlueZ
You will need to disable the BlueZ _HID Input_ plugin that normally hogs the HID
channels and the _PNAT_ plugin that seems to cause connection problems in
combination with python (resulting in regular security blocks when trying to
reconnect).
* __BlueZ 4__: Make sure to add `DisablePlugins = input,pnat` to
  `/etc/bluetooth/main.conf`
* __BlueZ 5__: Update the command line in `/lib/systemd/system/bluetooth.service`
  to `ExecStart=/usr/lib/bluetooth/bluetoothd --noplugin=input,pnat`

Afterwards you need to restart the bluetooth daemon. Depending on your bluetooth
controller you may need to manually power on your HCI device and make it
discoverable using the `hciconfig hci0 up pscan` command (you can also add this
command to your `/etc/rc.local` file).

## Usage
To establish a connection and start listening for button events on the bluetooth
device you first need to create a remote device object, and connect it to the
MAC address of your __local__ bluetooth controller if you are listening for
incoming connections or the MAC address of your __remote__ bluetooth device if
you are trying to establish a direct connection. Starting the `event_loop` will
then listen for button events until it has been idle for the amount of second
specified by `timeout`.
```python
remote = FireRemote(_DEVICE_MAC if connect else _CONTROLLER_MAC)
remote.connect(remote.MODE_CONNECT if connect else remote.MODE_LISTEN, timeout)
remote.event_loop()
```

### Event Callbacks
You can listen for button events using the `remote.events.listen(callback,
direction)` method of your remote device, where the direction parameter
specifies whether the callback is fired when the button is pressed (`down`) or
released (`up`).

### Implementing additional bluetooth devices/other remotes
Bluetooth HID devices are implemented as classes that inherit from `HIDDevice`
and implement some kind of `event_loop` method that calls `self.bluetooth_hid.
listen(callback)`. This method expects a callback function to evaluate the input
report and calls the `self.events.fire(keys)` method with a list of all keys
that are currently pressed.

## Examples
Some example scripts can be found in the `examples` folder, you will need to
replace the `_DEVICE_MAC` and `_CONTROLLER_MAC` values with the MAC address of
your remote device and your local bluetooth controller before running them.
* `examples/logevents.py`: Connect to the remote control and print button events
* `examples/kodi.py <ip>`: Implementation of the Kodi EventClient to relay button
  events to a Kodi Media Center running on a remote host

## Dependencies
As the bluetooth connection relies on native bluetooth sockets, Python 3.3+ is
required.
The example scripts require the `plac` module to parse command line arguments.

## Errors and Workarounds
* `Permission denied (13)`: Binding a bluetooth socket to a port may require to
  be run with as root (i.e. try to run the script again with `sudo`)
* `Address already in use (98)`: BlueZ input plugin needs to be disabled
  (see _Setup_)

## Misc.
Everything in the `tools` folder is most likely outdated and definitely not
needed any more. Therefore you can just ignore it.
