from bluetooth import _bluetooth as bluez

rx = bluez.hci_open_dev(0)
# save current filter
old_filter = rx.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)
flt = bluez.hci_filter_new()
bluez.hci_filter_set_ptype(flt, bluez.HCI_ACLDATA_PKT)
rx.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )
    
while True:
    message = rx.recv(1024)
    if message:
        message = [ord(c) for c in message]
        print "> HCI:", ' '.join(str(format(c, '02x')) for c in message)
