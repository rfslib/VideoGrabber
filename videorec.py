"""
    file: videorec.py
    author: ed c
"""

# TODO: warn on version mismatch for OBS, websockets and simpleobsws
# TODO: catch errors
# TODO: automatic file naming
# TODO: show filename of current recording
# TODO: installer
# TODO: show OBS info on F1?
# DONE: Show available disk space
# DONE: warn on low disk space
# DONE: disable buttons when not valid

import asyncio
import simpleobsws
from tkinter import *
import psutil
import subprocess
from time import sleep

debug = False

vr_title = 'RFSL Video Recorder'
vr_geometry = '450x250+48+48'

default_bg = 'SystemButtonFace'

obs_command = r'C:\Program Files\obs-studio\bin\64bit\obs64.exe'
obs_directory = ''

btn_font = 'Lucida Console'
btn_font_size = 16
btn_height = 3
btn_width = 8

st_font = 'Lucida Console'
st_font_size = 16

free_disk = 0.0
free_disk_min = 5000.0
fd_font = 'Lucida Console'
fd_font_size = 12
fd_delay = 60000

obs_version = ''
ws_version = ''


async def get_obs_info( ):
    await ws.connect()
    info = await ws.call( 'GetVersion' )
    if debug: print( f'GetVersion: {info}')
    obs_version = info[ 'obs-studio-version' ]
    ws_version = info[ 'obs-websocket-version' ]
    await asyncio.sleep( 1 )
    await ws.disconnect()

async def get_obs_disk_space( ):
    global free_disk
    await ws.connect( )
    stats = await ws.call( 'GetStats' )
    if debug: print( f'GetStats: {stats}')
    free_disk = float( stats[ 'stats' ][ 'free-disk-space' ] )
    await asyncio.sleep( 1 )
    await ws.disconnect( )
       
def show_disk_space( ):
    global free_disk
    loopy.run_until_complete( get_obs_disk_space() )
    if free_disk < free_disk_min:
        ds.config( bg = 'Red' )
    else:
        ds.config( bg = default_bg )
    disk_space_text.set( f' Available disk space: {free_disk/1024:.2f}G ' )
    vr.after( fd_delay, show_disk_space ) # 60000 for once a minute

async def __start_recording( ):
    await ws.connect()
    rc = await ws.call( 'StartRecording' )
    
    print( f'start_recording rc: {rc}')
    await asyncio.sleep( 1 )
    await ws.disconnect( )

def start_recording( ):
    btn_start[ 'state' ] = DISABLED
    loopy.run_until_complete( __start_recording( ) )
    lf.config( fg = 'Red')
    show_recording_status( 'Recording' )
    btn_stop[ 'state' ] = NORMAL

async def __stop_recording( ):
    await ws.connect()
    rc = await ws.call( 'StopRecording' )    
    print( f'stop_recording rc: {rc}')
    await asyncio.sleep( 1 )
    await ws.disconnect( )

def stop_recording( ):
    btn_stop[ 'state' ] = DISABLED
    loopy.run_until_complete( __stop_recording( ) )
    lf.config( fg = 'Black')
    show_recording_status( 'Stopped' )
    btn_start[ 'state' ] = NORMAL

def show_recording_status( txt ): # Show status message next to buttons
    recording_status.set( txt )

def is_process_running( processName ): # https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/
    '''
    Check if there is any running process that contains the given name processName.
    '''
    for proc in psutil.process_iter(): #Iterate over the all the running processes
        try:
            if processName.lower() in proc.name().lower(): # Check if process name contains the given name string
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            return False
    
#------
if __name__ == '__main__':
    vr = Tk()
    vr.geometry( vr_geometry )
    vr.resizable( False, False )
    vr.title( vr_title )
    vr.iconbitmap( 'VideoRec.ico' )
    #vr.config( bg='LightBlue' )
    vr.attributes( '-topmost', 1 ) # force it to stay on top (so user doesn't lose it)

    # frame/label for status
    sf = Frame( master=vr, padx=8, pady=8 )
    sf.grid( row=0, column=3, padx=4, pady=4)
    recording_status = StringVar()
    lf = Label( sf, textvariable=recording_status, font=( st_font, st_font_size ) )
    lf.grid()
    

    # frame for start button
    fr1 = Frame( master=vr, padx = 8, pady = 8 )
    fr1.grid( row=0, column=1, padx = 4, pady = 4, sticky='wn' )

    # create 'start' button
    btn_start = Button( fr1, text = 'Record',
        height=btn_height, width=btn_width,
        command = start_recording,
        font = ( btn_font, btn_font_size ),
        fg='Red'
        )
    btn_start.grid( row=1, column=1 )

     # frame for stop
    fr2 = Frame( master=vr, padx = 8, pady = 8 )
    fr2.grid( row=0, column=2, padx = 4, pady = 4, sticky='en' )
   
    # create 'stop' button
    btn_stop = Button( fr2, text = 'Stop',
        height=btn_height, width=btn_width,
        command = stop_recording,
        state = DISABLED,
        font = ( btn_font, btn_font_size )
        )
    btn_stop.grid( row=1, column=1)

    # frame/label for disk space
    fr3 = Frame( master=vr, padx = 8, pady = 8 )
    fr3.grid( row = 1, column=1, columnspan=3 )
    disk_space_text = StringVar()
    ds = Label( fr3, textvariable=disk_space_text, font=( fd_font, fd_font_size ) )
    ds.grid( )
    print( f'default background color: {ds.cget( "background" )}')

    # if OBS isn't running, start it
    if not is_process_running( 'obs64.exe' ):
        try:
            subprocess.Popen( obs_command, cwd = obs_directory )
        except:
            show_recording_status( 'OBS not found' )
            print( 'ERROR:\nOBS not found' )
            sleep( 8 )
            exit( )

    # set up an interface to OBS Studio
    loopy = asyncio.get_event_loop()
    ws = simpleobsws.obsws(host='127.0.0.1', port=4444, password='family', loop=loopy)
    loopy.run_until_complete( get_obs_info ( ) )

    show_disk_space() # re-runs itself every fd_delay milliseconds (default one minute)

    if debug: print( 'all set; entering the tk forever loop' )

    vr.mainloop()
