import time
import threading

from beacontools import BeaconScanner, IBeaconFilter, IBeaconAdvertisement

PERIOD=5

period=PERIOD


def callback(bt_addr, rssi, packet, additional_info):
    print("TEST")
    # scanner._mon.toggle_scan(False)
    sg=additional_info['minor']/1000
    t_f=additional_info['major']
    grav_p=135.997*(sg**3) - 630.272 * (sg**2) + 1111.14 * sg - 616.868
    temp_c= (t_f - 32 ) * 5/9. 


scanner = BeaconScanner(callback,
            packet_filter=IBeaconAdvertisement
            )

scanner.start()

while True:
    print("a")
    time.sleep(period)
    scanner._mon.toggle_scan(True)




