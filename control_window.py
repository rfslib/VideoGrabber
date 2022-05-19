"""
    file: control_window.py
    author: ed c
"""

from tkinter import *

class Control_Window( Toplevel ):

    debug = 1

    # visuals
    start_btn_txt = 'Start Session'
    start_btn_height = 4
    start_btn_fontsize = 12

    ## attributes of the control window
    moffsetx = 0
    moffsety = 0
    ttl = 'Story Room'       # title
    font = 'Lucida Console'    # primary font for text
    fontsize = 48              # font size
    fontcolor = '#100010'
    bgcolor = '#efffef'             # background color
    padxy = 4                   # padding inside of frames
    

    def __init__(self, master):
        Toplevel.__init__(self,master)

        # set our look
        self.config( bg=self.bgcolor)
        self.overrideredirect( True )
    
        # get our size and location
        self.mwidth = self.winfo_screenwidth( )
        self.mheight = self.winfo_screenheight( )
        self.geometry( f'{self.mwidth}x{self.mheight}+{self.moffsetx}+{self.moffsety}')

        # set up the window's "title" frame
        self.ttlframe = Frame( master=self,
            relief = RIDGE, borderwidth = 5, bg=self.bgcolor,
            padx = self.padxy, pady = self.padxy )
        self.ttlframe.grid( row=0, column=0, padx = self.padxy, pady = self.padxy, sticky='ew' )
        self.grid_columnconfigure( 0, weight=1 )
        Label( master=self.ttlframe, # width=30,
            text=self.ttl, font=('Lucida Console', self.fontsize), bg=self.bgcolor, fg=self.fontcolor,
            ).pack( padx = self.padxy, pady = self.padxy)

        # create a frame for interactions (buttons, text entry, etc.)
        self.btnframe = Frame( master=self, 
            padx = self.padxy, pady = self.padxy )
        self.btnframe.grid( row=1, column=0, padx = self.padxy, pady = self.padxy, sticky='ewn' )
        #Label( master=self.btnframe, text='' ).pack( padx = self.padxy, pady = self.padxy )
              
        self.ctrl_strt= Button( self.btnframe, text = self.start_btn_txt,
            height=self.start_btn_height,
            command = self.start_session,
            font = ( self.font, self.start_btn_fontsize ) ).pack()

        if self.debug: print( 'control window ready' )

    def start_session( self ):
        
        pass
    

if __name__ == '__main__':
    root = Tk()
    root.geometry( '300x100+0+0' )
    root.title( 'close me to exit test' )
    tst = Control_Window( root )
    root.mainloop()