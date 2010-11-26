#!/bin/python

class Guide:

    TURNING_ANGLE = Math.PI / 4
    STEP = 0.5

    def __init__(self):
        self.data = []

    def replan(self):
        if _hasBeenStarted:
            Context.enqueueMessage("Hold on while I get oriented, please.")
        else:
            _hasBeenStarted = True
            Context.enqueue("OK, let's start")

        realizer.clearAlarms()

