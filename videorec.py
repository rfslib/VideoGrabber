"""
    file: videorec.py
    author: Ed C


    purpose: start Tk and set up windows for control of the VHS/Video8 recording systems
            meant to run continuously
"""

from tkinter import *
from control_window import Control_Window
#from timer_window import Timer_Window

debug = 1

def callback_test( ):
    print( 'callback called :)')
    timer_win.set_txt( 'YAY!')
    timer_win.start_countdown( 'remaining minutes: {}', 120, 60, 60, callback_test )


root = Tk()

if debug: # show the root window so it can be closed to exit the test
    root.geometry( '400x100+0+0' )
    root.title( 'Close me to shut down the test' )
else: # but normally hide the root window
    root.withdraw()

control_win = Control_Window( root )

root.mainloop() # make Tk work

