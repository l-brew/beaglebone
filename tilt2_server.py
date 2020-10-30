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
    def __init__(self,scan_complete=None,period=PERIOD):
        self.scanner = None
        self.grav_p = None
        self.temp_c = None
        self.period=PERIOD
        self.scan_complete=None

    def start(self):

        def callback(bt_addr, rssi, packet, additional_info):
            self.scanner._mon.toggle_scan(False)
            sg=additional_info['minor']/1000
            t_f=additional_info['major']
            self.grav_p=135.997*(sg**3) - 630.272 * (sg**2) + 1111.14 * sg - 616.868
            self.temp_c= (t_f - 32 ) * 5/9. 
            if self.scan_complete:
                self.scan_complete(self)


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

class server:
    def __init__(self,server_address="/tmp/tilt2_socket"):
        self.server_address = server_address
        
    def open_socket(self):
        try:
            os.unlink(self.server_address)
        except OSError:
            if os.path.exists(self.server_address):
                raise


        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # Bind the socket to the port
        self.sock.bind(self.server_address)
        os.chmod(self.server_address, 0o777)
        self.sock.listen(1)
        print("opened socket to %s" % self.server_address)

    def wait_for_client(self):
        self.connection, self.client_address = self.sock.accept()

    def send(self,message):
            self.connection.sendall(bytes(message,'utf-8'))



if __name__=="__main__":
    svr=server()

    svr.open_socket()
    print("wait for client")
    svr.wait_for_client()

    def scan_complete(t):
        msg={"tmp":t.temp_c or float("inf") , "grav":t.grav_p or float("inf") }
        try:
            svr.send(json.dumps(msg))
        except BrokenPipeError:
            svr.wait_for_client()

    t=Tilt2(scan_complete)
    t.start()

    # while True:
        # time.sleep(PERIOD)


