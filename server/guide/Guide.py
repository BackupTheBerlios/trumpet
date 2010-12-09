#!/bin/python

class Guide:

    World world
    State state
    Dictator
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

        #Remove alarms
        realizer.clearAlarms()

        #Add Alarm-warning alarms
        atoms = Context.getWorld().getTrueAtoms();
        for a in atoms:
            if a.getPredicate() == 'alarm':
                name = (str)a.getArgs()[0]
                alarm = new AlarmWarning

