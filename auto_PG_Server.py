import logging
import sys
import time

import numpy
import tango
from tango import DispLevel, AttrWriteType, DevState
from tango.server import attribute, command

sys.path.append('../TangoUtils')
from TangoServerPrototype import TangoServerPrototype
from TangoUtils import Configuration
from config_logger import config_logger
from log_exception import log_exception

t0 = time.time()
OFF_PASSWORD = 'topsecret'


class RFPowerPGcurrent(TangoServerPrototype):
    server_version = '0.0'
    server_name = 'Python server increases PG Current proportionaly to RF power'
    device_list = []

    MAX_RF_power = attribute(label="MAX_RF_POWER", dtype=float,
                            display_level=DispLevel.OPERATOR,
                            access=AttrWriteType.READ_WRITE,
                            unit="kW", format="%f",
                            doc="MAX_RF_POWER")

    MAX_PG_current = attribute(label="MAX_PG_CURRENT", dtype=float,
                             display_level=DispLevel.OPERATOR,
                             access=AttrWriteType.READ_WRITE,
                             unit="A", format="%f",
                             doc="MAX_PG_current")

    server_sleep_time = attribute(label="server_sleep_time", dtype=float,
                               display_level=DispLevel.OPERATOR,
                               access=AttrWriteType.READ_WRITE,
                               unit="A", format="%f",
                               doc="server_sleep_time")

    PG_current_start_stab = attribute(label="PG_current_stab", dtype=bool,
                               display_level=DispLevel.OPERATOR,
                               access=AttrWriteType.READ_WRITE,
                               unit="", format="%s",
                               doc="start change PG current proportionaly to RF power")


    def init_device(self):
        # devices
        self.adc = tango.DeviceProxy('binp/nbi/adc0')
        self.TDK = tango.DeviceProxy('binp/nbi/adc0')
        # attribute values
        self.dT = 1.0
        self.rf_power = 65.0
        self.pg_current = 50.0
        #
        super().init_device()
        RFPowerPGcurrent.device_list.append(self)

    def read_power_limit(self):
        return self.power_limit_value

    def write_power_limit(self, value):
        self.power_limit_value = value
        self.config['power_limit'] = value








def looping():
    global t0
    time.sleep(0.1)
    for dev in RFPowerPGcurrent.device_list:
        time.sleep(0.001)
        try:
            if dev.get_state() != DevState.RUNNING:
                continue
            p = dev.calculate_anode_power()
            if p > dev.power_limit_value:
                dev.error('Anode power limit exceeded')
                dev.pulse_off(OFF_PASSWORD)
        except:
            dev.log_exception('Error in loop')


if __name__ == "__main__":
    RFPowerPGcurrent.run_server(event_loop=looping)
    # RFPowerTangoServer.run_server()
