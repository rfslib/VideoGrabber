"""
    file: videorec.py
    author: ed c
"""
import asyncio
from cmath import e
from operator import is_
import simpleobsws
from tkinter import *
import psutil
import subprocess
from time import sleep

debug = True

btn_font = 'Lucida Console'
btn_font_size = 16
btn_height = 3
btn_width = 8

st_font = 'Lucida Console'
st_font_size = 16

obs_version = ''
ws_version = ''
free_disk = ''

async def get_obs_info( ):
    await ws.connect()
    info = await ws.call( 'GetVersion' )
    if debug: print( f'GetVersion: {info}')
    obs_version = info[ 'obs-studio-version' ]
    ws_version = info[ 'obs-websocket-version' ]
    stats = await ws.call( 'GetStats' )
    if debug: print( f'GetStats: {stats}')
    free_disk = float( stats[ 'stats' ][ 'free-disk-space' ] )
    await asyncio.sleep( 1 )
    await ws.disconnect()


async def __start_recording( ):
    await ws.connect()
    rc = await ws.call( 'StartRecording' )
    show_recording_status( 'Recording' )
    print( f'start_recording rc: {rc}')
    await asyncio.sleep( 1 )
    await ws.disconnect( )

def start_recording( ):
    loopy.run_until_complete( __start_recording( ) )

async def __stop_recording( ):
    await ws.connect()
    rc = await ws.call( 'StopRecording' )
    show_recording_status( 'Stopped' )
    print( f'stop_recording rc: {rc}')
    await asyncio.sleep( 1 )
    await ws.disconnect( )

def stop_recording( ):
    loopy.run_until_complete( __stop_recording( ) )

def show_recording_status( txt ) :
    recording_status.set( txt )
    lf.update()

def is_process_running( processName ): # https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running processes
    for proc in psutil.process_iter():
        try:
            if processName.lower() in proc.name().lower(): # Check if process name contains the given name string
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            return False
    
#------
if __name__ == '__main__':
    vr = Tk()
    vr.geometry( '450x108+48+48' )
    vr.resizable( False, False )
    vr.title( 'Video Recorder' )
    vr.iconbitmap( 'VideoRec.ico' )
    #vr.config( bg='LightBlue' )
    vr.attributes( '-topmost', 1 )



    # frame for status
    sf = Frame( master=vr, padx=8, pady=8 )
    sf.grid( row=0, column=3, padx=4, pady=4)

    # label for status
    recording_status = StringVar()
    lf = Label( sf, textvariable=recording_status,
        
        font=( st_font, st_font_size ) )
    lf.grid()

    # frame for start button
    fr1 = Frame( master=vr, padx = 8, pady = 8 )
    fr1.grid( row=0, column=1, padx = 4, pady = 4, sticky='wn' )

    # create 'start' button
    Button( fr1, text = 'Record',
        height=btn_height, width=btn_width,
        command = start_recording,
        font = ( btn_font, btn_font_size ),
        fg='Red'
        ).grid( row=1, column=1 )

     # frame for stop
    fr2 = Frame( master=vr, padx = 8, pady = 8 )
    fr2.grid( row=0, column=2, padx = 4, pady = 4, sticky='en' )
   
    # create 'stop' button
    Button( fr2, text = 'Stop',
        height=btn_height, width=btn_width,
        command = stop_recording,
        font = ( btn_font, btn_font_size )
        ).grid( row=1, column=1)

    # if OBS isn't running, start it
    if not is_process_running( 'obs64.exe' ):
        try:
            #TODO: needs to start in the directory where the executable is found
            #subprocess.Popen( ['"C:/Program Files/obs-studio/bin/64bit/obs64.exe"'])
            subprocess.Popen( r'C:\Program Files\obs-studio\bin\64bit\obs64.exe', cwd=r'C:\Program Files\obs-studio\bin\64bit')
        except:
            show_recording_status( 'OBS not found' )
            print( 'ERROR:\nOBS not found' )
            sleep( 8 )
            exit( )

    # set up an interface to OBS Studio
    loopy = asyncio.get_event_loop()
    ws = simpleobsws.obsws(host='127.0.0.1', port=4444, password='family', loop=loopy)
    loopy.run_until_complete( get_obs_info ( ) )

    # show OBS info

    vr.mainloop()
