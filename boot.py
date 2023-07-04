
import network
from time import sleep
from secrets import secrets
import machine

def do_connect():
    wlan = network.WLAN(network.STA_IF)         # Put modem on Station mode

    if not wlan.isconnected():                  # Check if already connected
        print('Connecting to network...')
        wlan.active(True)                       # Activate network interface
        wlan.config(pm = 0xa11140)              # Set power mode to get WiFi power-saving off (if needed)
        wlan.connect(secrets["ssid"], secrets["password"])  # WiFi Credential
        print('Waiting for connection...', end='')
        # Check if it is connected otherwise wait
        while not wlan.isconnected() and wlan.status() >= 0:
            print('.', end='')
            sleep(1)
    elif wlan.isconnected():
        print("Already connected.")
    # Print the IP assigned by router
    ip = wlan.ifconfig()[0]
    print('\nConnected on {}'.format(ip))
    return ip 

try:
    ip = do_connect()
except KeyboardInterrupt:
    print("Keyboard interrupt")
