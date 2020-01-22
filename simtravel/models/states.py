# -*- coding: utf-8 -*-
from enum import Enum


class States(Enum):
    TOWARDS_DEST = 0
    AT_DEST = 1
    TOWARDS_ST = 2
    QUEUEING = 3
    CHARGING = 4
    NO_BATTERY = 5
    def moving_states():
        return [States.TOWARDS_DEST, States.TOWARDS_ST]
    def idle_states(self):
        return [States.CHARGING, States.QUEUEING, States.AT_DEST]
