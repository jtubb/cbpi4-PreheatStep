import asyncio
import random
import logging
from cbpi.api import *
from cbpi.api.base import CBPiBase
from cbpi.api.dataclasses import Kettle, Props, Fermenter

import subprocess
import os
import board
import busio
from numpy import interp
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

logger = logging.getLogger(__name__)
        
def getI2CDevices():
    try:
        devarr = []
        i2c = busio.I2C(board.SCL, board.SDA)
        devarr = [hex(int(x)) for x in i2c.scan()]
        filter_list=['0x48', '0x49', '0x4a', '0x4b']
        devarr = list(filter(lambda x: any([x.find(y) == 0 for y in filter_list]), devarr))
        for device in devarr:
            logger.info("ADS1X15 ACTOR DEVICE DETECTED - ADDRESS %s" % (device))
        return devarr
    except Exception as e:
        logger.info("ADS1X15 ACTOR DETECT I2C BUS FAILED %s" % (e))
        return []



@parameters([Property.Select(label="Chip", options=["ADS1015","ADS1115"]),
             Property.Select(label="Address", options=getI2CDevices()),
             Property.Select(label="Channel", options=[0,1,2,3]),             
             Property.Number(label="Gain", options=[(2/3, 1, 2, 4, 8, 16)], description="GAIN    RANGE (V)<br>----    ---------<br>2/3    +/- 6.144<br>  1    +/- 4.096<br>  2    +/- 2.048<br>  4    +/- 1.024<br>  8    +/- 0.512<br> 16    +/- 0.256"), 
             Property.Number(label="Min_Range", configurable=True, default_value=0, description="Sensor value to map to 0"), 
             Property.Number(label="Max_Range", configurable=True, default_value=4095, description="Sensor value to map to 100"),
             Property.Select(label="Read_Mode", options=["Voltage","Raw","Ranged"], description="Output Raw Value or Range from 0-100")])
             
             
class ADS1X15Sensor(CBPiSensor):

    def __init__(self, cbpi, id, props):
        super(CustomSensor, self).__init__(cbpi, id, props)
        i2c = busio.I2C(board.SCL, board.SDA)
        if(self.props.Chip == "ADS1115"):
            ads = ADS.ADS1115(i2c, address=self.props.Address)
        else:
            ads = ADS.ADS1015(i2c, address=self.props.Address)
        match self.props.Channel:
            if(self.props.Channel==0):
                self.dev = AnalogIn(ads, ADS.P0)
            else if(self.props.Channel==1):
                self.dev = AnalogIn(ads, ADS.P1)
            else if(self.props.Channel==2):
                self.dev = AnalogIn(ads, ADS.P2)
            else if(self.props.Channel==3):
                self.dev = AnalogIn(ads, ADS.P3)
        self.value = 0

    async def run(self):
        while self.running:
            self.value = self.dev.value
            if (self.props.Read_Mode=="Voltage")":
                self.value = self.dev.voltage
            if(self.props.Read_Mode=="Ranged"):
                self.value = int(interp(self.value, [0, 100], [int(self.props.Min_Range), int(self.props.Max_Range)]));
            self.log_data(self.value)
            self.push_update(self.value)
            await asyncio.sleep(1)

    def get_state(self):
        return dict(value=self.value)

def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''
    try:
        subprocess.run(["modprobe","i2c-bcm2835"])
        subprocess.run(["modprobe","i2c-dev"])
    except Exception as e:
        logger.info("ADS1X15 ACTOR MODPROBE FAILED %s" % (e))
        pass
        
    cbpi.plugin.register("ADS1X15Sensor", ADS1X15Sensor)
