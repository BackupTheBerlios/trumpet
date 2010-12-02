#!/usr/bin/python
import picke

class Comm:
    ''' Method that translate string to bytes'''
    def text2byte(self,text):
        pickled  = picke.dumps(a)
        unpickled = pickle.loads(pickled)

    #Lista de mensajes posibles:
        #1 login (no params)
        #2 logout(no params)
        #3 move forward (no params)
        #4 move backwards (no params)
        #5 move left (no params)
        #6 move right (no params)
        #7 rotate left (no params)
        #8 rotate right (no params)
        #9 set position (position)
        #10 get position (position)
        #11 set destination (position)
        #12 ask guide for instructions (no param)
        #13 give instructions (instructions)
        #14 not found (no params)
        #15 forbidden (no params)
        #16 question malformed (no params)

        
