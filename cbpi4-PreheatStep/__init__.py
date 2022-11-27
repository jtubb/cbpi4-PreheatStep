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
        logger.info("ADS1X15 ACTOR DETECT I2C BUS FAILED - %s" % (e))
        return []



@parameters([Property.Select(label="Chip", options=["ADS1015","ADS1115"]),
             Property.Select(label="Address", options=getI2CDevices()),
             Property.Select(label="Channel", options=[0,1,2,3]),             
             Property.Select(label="Gain", options=["2/3", "1", "2", "4", "8", "16"], description="Gain Range"), 
             Property.Number(label="Min_Range", configurable=True, default_value=0, description="Sensor value to map to 0"), 
             Property.Number(label="Max_Range", configurable=True, default_value=4095, description="Sensor value to map to 100"),
             Property.Select(label="Read_Mode", options=["Voltage","Raw","Ranged"], description="Output Raw Value or Range from 0-100"),
             Property.Select(label="Interval", options=[1,5,10,30,60], description="Interval in Seconds")])

             
class ADS1X15Sensor(CBPiSensor):

    def __init__(self, cbpi, id, props):
        super(ADS1X15Sensor, self).__init__(cbpi, id, props)
        self.props.Sensor = self.props.get("Chip")+" "+self.props.get("Address")+"-"+str(self.props.get("Channel"))
        i2c = busio.I2C(board.SCL, board.SDA)
        if(self.props.get("Chip","ADS1115") == "ADS1115"):
            ads = ADS.ADS1115(i2c, address=int(self.props.get("Address"), 16))
        else:
            ads = ADS.ADS1015(i2c, address=int(self.props.get("Address"), 16))
        try:
            ads.gain = int(self.props.get("Gain","1"))
        except:
            ads.gain = 2/3
        self.dev = AnalogIn(ads, ADS.P0)
        if(self.props.get("Channel",0)==1):
            self.dev = AnalogIn(ads, ADS.P1)
        elif(self.props.get("Channel",0)==2):
            self.dev = AnalogIn(ads, ADS.P2)
        elif(self.props.get("Channel",0)==3):
            self.dev = AnalogIn(ads, ADS.P3)
        self.value = 0

    async def run(self):
        while self.running:
            self.value = self.dev.value
            if (self.props.get("Read_Mode","Raw")=="Voltage"):
                self.value = self.dev.voltage
            if(self.props.get("Read_Mode","Raw")=="Ranged"):
                self.value = int(interp(self.value, [0, 100], [int(self.props.get("Min_Range",0)), int(self.props.get("Max_Range",4096))]));
            self.log_data(self.value)
            self.push_update(self.value)
            await asyncio.sleep(self.props.get("Interval",5))

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
