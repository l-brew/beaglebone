import socket
import sys
import json
import time
import threading
import time
import threading

from beacontools import BeaconScanner, IBeaconFilter, IBeaconAdvertisement

from bleak import discover
import asyncio


import socket
import sys
import os

import json


PERIOD=5

class Tilt2:
    def __init__(self):
        self.temp=None
        self.grav = None
        self.scanner = None
        self.period=PERIOD
        self.scan_complete=None
        pass

    def connect(self):
        self.start()

        
    def start(self):

        def callback(bt_addr, rssi, packet, additional_info):
            self.scanner._mon.toggle_scan(False)
            sg=additional_info['minor']/1000
            t_f=additional_info['major']
            self.grav=135.997*(sg**3) - 630.272 * (sg**2) + 1111.14 * sg - 616.868
            self.temp= (t_f - 32 ) * 5/9. 


        self.scanner = BeaconScanner(callback,
                    packet_filter=IBeaconAdvertisement
                    )

        async def run():
            devices = await discover()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(run())


        self.scanner.start()

        def _run():
            while True:
                time.sleep(self.period)
                self.scanner._mon.toggle_scan(True)

        threading.Thread(target=_run).start()

      



  


