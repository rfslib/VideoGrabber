"""
    file: videograbber.py
    author: ed c

    obs websocket doc: https://github.com/obsproject/obs-websocket/blob/4.x-current/docs/generated/protocol.md
"""

# TODO: OBS Event: 'SourceDestroyed', Raw data: {'sourceKind': 'scene', 'sourceName': 'Scene', 'sourceType': 'scene', 'update-type': 'SourceDestroyed'}: close app
# TODO: use OS instead of OBS to get disk space (so no exception if obs is closed and disk space wants to be updated)
# TODO: consider closing preview and using projector instead
# TODO: catch events
# TODO: installer (installation instructions)
# TODO: (OBS) create sources, lock configuration files
# TODO: check, set Sources, Profile, Scene (create standards for these)
# TODO: set filename format (SetFilenameFormatting)
# TODO: QSG (have this app set all parameters so no manual settings are required)
# TODO: warn on version mismatch for OBS, websockets and simpleobsws
# TODO: catch errors
# TODO: USB disconnect
# TODO: OBS status, Popen.wait(), Popen.poll() (https://docs.python.org/3/library/subprocess.html)
# XXXX: automatic file naming
# DONE: show elapsed recording time
# DONE: show OBS recording time on stop recording (use GetRecordingStatus before stopping)
# DONE: show filename of current recording
# DONE: show OBS info on F1?
# DONE: Show available disk space
# DONE: warn on low disk space
# DONE: disable buttons when not valid

import asyncio
from asyncio.windows_events import NULL
from tabnanny import check
import simpleobsws
from tkinter import *
import psutil
import subprocess
from datetime import timedelta
from os.path import basename

debug = True

expected_obs_version = '27.2.4'
expected_ws_version = '4.9.1'
expected_simpleobsws_version = '1.1'

vr_title = 'Riverton FamilySearch Library Video Grabber'
vr_geometry = '500x180+48+48'

bg_color = 'SystemButtonFace'
bg_alpha = 0.95

obs_command = r'C:\Program Files\obs-studio\bin\64bit\obs64.exe'
obs_directory = r'C:\Program Files\obs-studio\bin\64bit'
obs_startup_parms = r'--minimize-to-tray'

btn_font = 'Lucida Console'
btn_font_size = 16
btn_height = 3
btn_width = 8

st_font = 'Lucida Console'
st_font_size = 16


recording_filename_font = 'Lucida Console'
recording_filename_fontsize = 9

recording_in_progress = False
elapsed_time = 0
elapsed_time_font = 'Lucida Console'
elapsed_time_fontsize = 9
elapsed_time_after = NULL

free_disk = 0.0
free_disk_min = 5000.0
fd_font = 'Lucida Console'
fd_font_size = 12
fd_delay = 60000  # 60000 to update available disk space once a minute

app_status_font = 'Lucida Console'
app_status_font_size = 10

obs_pswd = 'family'
obs_version = ''
obs_status = ''
ws_version = ''


async def get_obs_info( ):
    global obs_version, obs_status, ws_version
    ##await ws.connect()
    info = await ws.call( 'GetVersion' )
    if debug: print( f'GetVersion: {info}')
    obs_version = info[ 'obs-studio-version' ]
    ws_version = info[ 'obs-websocket-version' ]
    obs_status = info[ 'status' ]
    await asyncio.sleep( 1 )
    ##await ws.disconnect()
    if debug: print( f'obs: {obs_version}, ws: {ws_version}, status: {obs_status}')

async def get_obs_disk_space( ):
    global free_disk
    ##await ws.connect( )
    stats = await ws.call( 'GetStats' )
    if debug: print( f'GetStats: {stats}')
    free_disk = float( stats[ 'stats' ][ 'free-disk-space' ] )
    await asyncio.sleep( 1 )
    ##await ws.disconnect( )
       
def show_disk_space( ):
    global free_disk
    loopy.run_until_complete( get_obs_disk_space() )
    if free_disk < free_disk_min:
        ds.config( bg = 'Red' )
    else:
        ds.config( bg = bg_color )
    disk_space_text.set( f'Available disk space: {free_disk/1024:.1f}G ' )
    vr.after( fd_delay, show_disk_space )

async def __start_recording( ):
    ##await ws.connect()
    rc = await ws.call( 'StartRecording' )   
    if debug: print( f'start_recording rc: {rc}')
    await asyncio.sleep( 1 )
    info = await( ws.call( 'GetRecordingStatus' ) )
    recording_filename.set( basename( info[ 'recordingFilename' ] ) )
    ##await ws.disconnect( )

def start_recording( ):
    global recording_in_progress, elapsed_time
    btn_start[ 'state' ] = DISABLED
    show_app_status( 'Do NOT close OBS: the recording will fail', 'DarkRed' )
    recording_in_progress = True
    loopy.run_until_complete( __start_recording( ) )
    show_recording_status( 'Recording', 'Red' )
    elapsed_time = 0
    show_elapsed_time()
    btn_stop[ 'state' ] = NORMAL

async def __stop_recording( ):
    ##await ws.connect()
    # TODO: use GetRecordingStatus to get the length of the recording
    info = await( ws.call( 'GetRecordingStatus' ) )
    await asyncio.sleep( 1 )
    if debug: print( f'GetRecordingStatus.recordTimecode {info[ "recordTimecode" ]}')
    recording_time.set( info[ 'recordTimecode' ] )
    rc = await ws.call( 'StopRecording' )    
    if debug: print( f'stop_recording rc: {rc}')   
    ##await ws.disconnect( )

def stop_recording( ):
    global recording_in_progress, elapsed_time_after
    recording_in_progress = False
    vr.after_cancel( elapsed_time_after ) # stop the elapsed time counter and display
    btn_stop[ 'state' ] = DISABLED
    loopy.run_until_complete( __stop_recording( ) )    
    show_recording_status( 'Stopped', 'Black' )
    show_app_status( f'File "{recording_filename.get()}" saved to the desktop', 'Grey' )
    btn_start[ 'state' ] = NORMAL


def show_recording_status( txt, color ): # Show status message next to buttons
    recording_state_label.config( fg = color )
    recording_state.set( txt )

def show_app_status( txt, color='Grey' ):
    app_status.config( fg = color )
    app_status_text.set( txt )

def show_elapsed_time():
    global recording_in_progress, elapsed_time, elapsed_time_after
    if debug: print( f'show_elapsed_time: {elapsed_time}')
    if recording_in_progress:
        recording_time.set( str( timedelta( seconds=elapsed_time ) ) )
        elapsed_time += 1
        elapsed_time_after = vr.after( 1000, show_elapsed_time )
    #else:
        #recording_time.set( '' )


def is_process_running( processName ): # https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/
    ''' Check if there is any running process that contains the given name processName. '''
    for proc in psutil.process_iter(): #Iterate over the all the running processes
        try:
            if processName.lower() in proc.name().lower(): # Check if process name contains the given name string
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
        except (psutil.ZombieProcess):
            # TODO: need to kill it
            return False

def start_obs( ):
    global obs_command, obs_directory, obs_startup_parms
    try:
        subprocess.Popen( obs_command, cwd = obs_directory )
        return True
    except:
        btn_start[ 'state' ] = DISABLED
        btn_stop[ 'state' ] = DISABLED
        show_app_status( 'ERROR: OBS could not be started', 'Red' )
        if debug: print( 'ERROR: OBS could not be started' ) 
        return False

def check_obs( ):
    # if OBS isn't running, start it
    if not is_process_running( 'obs64.exe' ):
        if( start_obs() ):
            show_app_status( 'OBS is running' )
            return True
        else:
            show_app_status( 'ERROR: OBS could not be started', 'Red')
            btn_start[ 'state' ] = DISABLED
            btn_stop[ 'state' ] = DISABLED
            return False
    else:
        return True
        

async def start_obs_projector( ):
    ##await ws.connect()
    rc = await ws.call( 'OpenProjector' )   
    if debug: print( f'OpenProjector rc: {rc}')
    ##await ws.disconnect( )

async def __configure_obs( ):
    ##await ws.connect()
    #rc = await ws.call( 'SetFilenameFormatting' ) 
    #if debug: print( f'SetFilenameFormatting: {rc}') 
    # TODO: GetSourcesList, CreateSource, SetVolume, SetSourceSettings, SetCurrentProfile, ListProfiles, GetRecordingStatus, SetRecordingFolder, SetCurrentScene, CreateScene,  
    await asyncio.sleep( 1 )
    ##await ws.disconnect( )

def configure_obs( ):
    loopy.run_until_complete( __configure_obs( ) )

async def on_obs_event( data ):
    print( f'OBS Event: \'{data["update-type"]}\', Raw data: {data}')
    if data[ 'update-type' ] == 'SourceDestroyed':
        print( 'OBS closed, forcing exit' )
        show_app_status( 'OBS closed, forcing exit' )
        await asyncio.sleep( 3 )
        vr.destroy()
        exit( )

def log_callback( ): 
    pass  

#------
if __name__ == '__main__':
    vr = Tk()
    vr.attributes( '-alpha', bg_alpha ) # set transparency
    vr.attributes( '-topmost', 1 ) # force it to stay on top (so user doesn't lose it)
    vr.geometry( vr_geometry )
    vr.resizable( False, False )
    vr.title( vr_title )
    vr.iconbitmap( 'VideoRec.ico' )  

    # frame for start button
    fr1 = Frame( master=vr, padx = 8, pady = 8 )
    fr1.grid( row=0, column=0, rowspan=3, padx = 4, pady = 4, sticky='wn' )

    # create 'start' button
    btn_start = Button( fr1, text = 'Record',
        height=btn_height, width=btn_width,
        command = start_recording,
        font = ( btn_font, btn_font_size ),
        fg='Red'
        )
    btn_start.grid( row=0, column=0 )

     # frame for stop
    fr2 = Frame( master=vr, padx = 8, pady = 8 )
    fr2.grid( row=0, column=1, rowspan=3, padx = 4, pady = 4, sticky='wn' )
   
    # create 'stop' button
    btn_stop = Button( fr2, text = 'Stop',
        height=btn_height, width=btn_width,
        command = stop_recording,
        state = DISABLED,
        font = ( btn_font, btn_font_size )
        )
    btn_stop.grid( row=0, column=0 )

    # frame/label for recording state, filename, time
    recording_state_frame = Frame( master=vr, padx=8, pady=8 )
    recording_state_frame.grid( row=0, column=2, padx=4, pady=4, sticky='wn')
    recording_state = StringVar()
    recording_state_label = Label( recording_state_frame, textvariable=recording_state, font=( st_font, st_font_size ), anchor='w' )
    recording_state_label.grid( sticky='w' )

    # frame/label for output filename
    #recording_filename_frame = Frame( master=vr, padx=8, pady=8 )
    #recording_filename_frame.grid( row=1, column=2, padx=4, pady=4, sticky='w')
    recording_filename = StringVar()
    recording_filename_label = Label( recording_state_frame, textvariable=recording_filename, font=( recording_filename_font, recording_filename_fontsize ), anchor='w' )
    recording_filename_label.grid( sticky='w')
    
    # frame/label for recording time
    #recording_time_frame = Frame( master=vr, padx=8, pady=8 )
    #recording_time_frame.grid( row=2, column=2, padx=4, pady=4, sticky='ws' )
    recording_time = StringVar()
    recording_time_label = Label( recording_state_frame, textvariable=recording_time, font=( elapsed_time_font, elapsed_time_fontsize ), anchor='w' )
    recording_time_label.grid( sticky='w' )

    # frame/label for disk space
    fr3 = Frame( master=vr, padx = 8, pady = 8 )
    fr3.grid( row = 3, column=0, columnspan=3, sticky='w' )
    disk_space_text = StringVar()
    ds = Label( fr3, textvariable=disk_space_text, font=( fd_font, fd_font_size ), anchor='w' )
    ds.grid( sticky='w')
    #if debug: print( f'default background color: {ds.cget( "background" )}')

    # frame/label for app status
    app_status_frame = Frame( master=vr, padx = 8, pady = 8 )
    app_status_frame.grid( row = 4, column=0, columnspan=3, sticky='w' )
    app_status_text = StringVar()
    app_status = Label( fr3, textvariable=app_status_text, font=( app_status_font, app_status_font_size ), anchor='w' )
    app_status.grid( sticky='w' )

    vr.update()

    if( check_obs( ) ): # if OBS start ok, then we can proceed
        # set up an interface to OBS Studio
        loopy = asyncio.get_event_loop()

        ws = simpleobsws.obsws(host='127.0.0.1', port=4444, password=obs_pswd, loop=loopy)
        loopy.run_until_complete( ws.connect() )
        ws.register( on_obs_event )

        loopy.run_until_complete( get_obs_info( ) )
        show_app_status( f'obs: {obs_version}, ws: {ws_version}, status: {obs_status}', 'Grey')

        vr.update()

        show_disk_space() # schedules itself to re-run every fd_delay milliseconds (default one minute)

        #loopy.run_until_complete( start_obs_projector( ) )
        
        if debug: print( 'all set; entering the tk forever loop' )
    else:
        show_app_status( 'ERROR: OBS could not be started. Restart me.', 'Red')

    vr.mainloop()
