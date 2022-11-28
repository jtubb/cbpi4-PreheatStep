
import asyncio
import aiohttp
from aiohttp import web
from cbpi.api.step import CBPiStep, StepResult
from cbpi.api.timer import Timer
from cbpi.api.dataclasses import Kettle, Props
from datetime import datetime
import time
from cbpi.api import *
import logging
from socket import timeout
from typing import KeysView
from cbpi.api.config import ConfigType
from cbpi.api.base import CBPiBase
from voluptuous.schema_builder import message
from cbpi.api.dataclasses import NotificationAction, NotificationType
import numpy as np
import requests
import warnings

@parameters([Property.Number(label="Temp", configurable=True),
             Property.Kettle(label="Kettle"),
             Property.Sensor(label="Sensor"),
             Property.Number(label="Min_Value", description="Sensor value must be higher than this to continue to the next step.", configurable=True),
             Property.Number(label="Max_Value", description="Sensor value must be lower than this to continue to the next step.", configurable=True)])

class PreheatStep(CBPiStep):

    async def NextStep(self, **kwargs):
        await self.next()

    async def on_timer_done(self,timer):
        self.summary = ""
        await self.push_update()

        self.cbpi.notify(self.name, "Preheating value set", NotificationType.SUCCESS)
        await self.next()

    async def on_timer_update(self,timer, seconds):
        await self.push_update()

    async def on_start(self):
        self.kettle=self.get_kettle(self.props.get("Kettle", None))
        if self.kettle is not None:
            self.kettle.target_temp = int(self.props.get("Temp", 0))
            await self.setAutoMode(True)
        self.summary = "Setting preheat temperature"
        if self.cbpi.kettle is not None and self.timer is None:
            self.timer = Timer(1 ,on_update=self.on_timer_update, on_done=self.on_timer_done)
        await self.push_update()

    async def on_stop(self):
        await self.timer.stop()
        self.summary = ""
        await self.push_update()

    async def run(self):
        while self.running == True:
            await asyncio.sleep(1)
            sensor_value=0
            if self.props.get("Sensor", None) is not None:
                sensor_value = self.get_sensor_value(self.props.get("Sensor", None)).get("value")
            if sensor_value >= int(self.props.get("Min_Value",-65535)) and sensor_value <= int(self.props.get("Max_Value",65535)) and self.timer.is_running is not True:
                self.timer.start()
                self.timer.is_running = True
            else:
                self.summary="Sensor interlock not met"
            await self.push_update()
        return StepResult.DONE

    async def setAutoMode(self, auto_state):
        try:
            if (self.kettle.instance is None or self.kettle.instance.state == False):
                await self.cbpi.kettle.toggle(self.kettle.id)
            await self.push_update()

        except Exception as e:
            logging.error("Failed to switch on KettleLogic {} {}".format(self.kettle.id, e))


class TimerStep(CBPiStep):
    @action("Add 5 Minutes to Timer", [])
    async def add_5_timer(self):
        if self.timer is not None and self.timer.is_running == True:
            self.cbpi.notify(self.name, '5 Minutes added', NotificationType.INFO)
            await self.timer.add(300)
            estimated_completion_time = datetime.fromtimestamp(self.timer.end_time)
            self.cbpi.notify(self.name, 'Timer started. Estimated Start: {}'.format(estimated_completion_time.strftime("%m/%d/%y %I:%M:%S %p")), NotificationType.INFO)
        else:
            self.cbpi.notify(self.name, 'Timer must be running to add time', NotificationType.WARNING)
    
    @action("Remove 5 Minutes from Timer", [])
    async def remove_5_timer(self):
        if self.timer is not None and self.timer.is_running == True:
            self.cbpi.notify(self.name, '5 Minutes removed', NotificationType.INFO)
            await self.timer.add(-300)
            estimated_completion_time = datetime.fromtimestamp(self.timer.end_time)
            self.cbpi.notify(self.name, 'Timer started. Estimated Start: {}'.format(estimated_completion_time.strftime("%m/%d/%y %I:%M:%S %p")), NotificationType.INFO)
        else:
            self.cbpi.notify(self.name, 'Timer must be running to add time', NotificationType.WARNING)
            
    @action("Add 30 Minutes to Timer", [])
    async def add_30_timer(self):
        if self.timer is not None and self.timer.is_running == True:
            self.cbpi.notify(self.name, '30 Minutes added', NotificationType.INFO)
            await self.timer.add(1800)
            estimated_completion_time = datetime.fromtimestamp(self.timer.end_time)
            self.cbpi.notify(self.name, 'Timer started. Estimated Start: {}'.format(estimated_completion_time.strftime("%m/%d/%y %I:%M:%S %p")), NotificationType.INFO)
        else:
            self.cbpi.notify(self.name, 'Timer must be running to add time', NotificationType.WARNING)
    
    @action("Remove 30 Minutes from Timer", [])
    async def remove_30_timer(self):
        if self.timer is not None and self.timer.is_running == True:
            self.cbpi.notify(self.name, '30 Minutes removed', NotificationType.INFO)
            await self.timer.add(-1800)
            estimated_completion_time = datetime.fromtimestamp(self.timer.end_time)
            self.cbpi.notify(self.name, 'Timer started. Estimated Start: {}'.format(estimated_completion_time.strftime("%m/%d/%y %I:%M:%S %p")), NotificationType.INFO)
        else:
            self.cbpi.notify(self.name, 'Timer must be running to add time', NotificationType.WARNING)
    
    async def NextStep(self, **kwargs):
        await self.next()

    async def on_timer_done(self,timer):
        self.summary = ""
        await self.push_update()

        self.cbpi.notify(self.name, "Starting Brew", NotificationType.SUCCESS)
        await self.next()

    async def on_timer_update(self,timer, seconds):
        self.summary = 'Estimated Start:\r\n{}'.format(datetime.fromtimestamp(time.time()+ (seconds)).strftime("%m/%d/%y %I:%M %p"))
        await self.push_update()

    async def on_start(self):
        self.summary = "Starting Brew Timer"
        if self.timer is None:
            self.timer = Timer(1800 ,on_update=self.on_timer_update, on_done=self.on_timer_done)
        else:
            self.timer.end_time = time.time()+1800
        await self.push_update()

    async def on_stop(self):
        await self.timer.stop()
        self.summary = ""
        await self.push_update()

    async def reset(self):
        self.timer = Timer(1800, on_update=self.on_timer_update, on_done=self.on_timer_done)
        
    async def run(self):
        while self.running == True:
            await asyncio.sleep(1)
            if self.timer.is_running is not True:
                self.timer.start()
                self.timer.is_running = True

        return StepResult.DONE
    
def setup(cbpi):
    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server

    :param cbpi: the cbpi core 
    :return: 
    '''    
    
    cbpi.plugin.register("PreheatStep", PreheatStep)
    cbpi.plugin.register("TimerStep", TimerStep)