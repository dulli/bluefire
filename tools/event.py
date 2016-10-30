
import os
import sys
import bluetooth
from bluetooth import *
import dbus
import time
import evdev
import binascii
from evdev import *

def send_input(ir):
    #  Convert the hex array to a string
    print ir
    hex_str = ""
    for element in ir:
      if type(element) is list:
        # This is our bit array - convrt it to a single byte represented
        # as a char
        bin_str = ""
        for bit in element:
          bin_str += str(bit)
        hex_str += chr(int(bin_str, 2))
      else:
        # This is a hex value - we can convert it straight to a char
        hex_str += chr(element)
    # Send an input report
    #message = [ord(c) for c in hex_str]
    #print ">", ' '.join(str(format(c, '02x')) for c in message)
    print hex_str
    print '------------'
    
class Keyboard():
  def __init__(self):
    # The structure for an bt keyboard input report (size is 10 bytes)
    self.state = [
         0xA1, # This is an input report
         0x01, # Usage report = Keyboard
         # Bit array for Modifier keys
         [0,   # Right GUI - (usually the Windows key)
          0,   # Right ALT
          0,   # Right Shift
          0,   # Right Control
          0,   # Left GUI - (again, usually the Windows key)
          0,   # Left ALT
          0,   # Left Shift
          0],   # Left Control
         0x00,  # Vendor reserved
         0x00,  # Rest is space for 6 keys
         0x00,
         0x00,
         0x00,
         0x00,
         0x00 ]

    # Keep trying to get a keyboard
    have_dev = False
    while have_dev == False:
      try:
        # Try and get a keyboard - should always be event0 as we.re only
        # plugging one thing in
        self.dev = InputDevice("/dev/input/event0")
        have_dev = True
      except OSError:
        print "Keyboard not found, waiting 3 seconds and retrying"
        time.sleep(3)
      print "Found a keyboard"
          
  def change_state(self, event):
      print event.code
      evdev_code = ecodes.KEY[event.code]
      print evdev_code
      hex_key = evdev_code
      # Loop through elements 4 to 9 of the input report structure
      for i in range (4, 10):
        if self.state[i] == hex_key and event.value == 0:
          # Code is 0 so we need to depress it
          self.state[i] = 0x00
          break
        elif self.state[i] == 0x00 and event.value == 1:
          # If the current space is empty and the key is being pressed
          self.state[i] = hex_key
          break

  def event_loop(self):
    for event in self.dev.read_loop():
      # Only bother if we hit a key and it's an up or down event
      if event.type == ecodes.EV_KEY and event.value < 2:
        self.change_state(event)
        send_input(self.state)
        
kb = Keyboard()
kb.event_loop()
