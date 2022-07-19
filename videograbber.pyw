"""
    file: videograbber.py
    author: rfslib

    obs websocket doc: https://github.com/obsproject/obs-websocket/blob/4.x-current/docs/generated/protocol.md
    simple xface to obs websocket: https://github.com/IRLToolkit/simpleobsws/tree/simpleobsws-4.x (included, since pip installs an incompatible version)
    starting a process from Python: https://docs.python.org/3/library/subprocess.html
    icon: https://stackoverflow.com/questions/14900510/changing-the-application-and-taskbar-icon-python-tkinter

"""

# TODO: OBS portable mode (config settings are saved in the OBS main folder) see obsproject.com/forum/resources/obs-and-obs-studio-portable-mode-on-windows.359
# TODO: OBS Event: 'SourceDestroyed', Raw data: {'sourceKind': 'scene', 'sourceName': 'Scene', 'sourceType': 'scene', 'update-type': 'SourceDestroyed'}: close app
# TODO: capture OS events (i.e., close app, etc.)
# TODO: consider closing preview and using projector instead
# TODO: catch OBS events
# TODO: installer (installation instructions)
# TODO: (OBS) create sources, lock configuration files
# TODO: check, set Sources, Profile, Scene (create standards for these)
# TODO: set filename format (SetFilenameFormatting)
# TODO: QSG (have this app set all parameters so no manual settings are required)
# TODO: warn on version mismatch for OBS, websockets and simpleobsws
# TODO: catch errors
# TODO: USB disconnect
# XXXX: OBS status, Popen.wait(), Popen.poll() (https://docs.python.org/3/library/subprocess.html)
# XXXX: Consider: start OBS (shell:startup) so it can't be changed by user/patron (but if it reboots...): start/stop a projector
# XXXX: automatic file naming
# DONE: use OS instead of OBS to get disk space (so no exception if obs is closed and disk space wants to be updated)
# DONE: Configuration file (use videograbber.json)
# DONE: show elapsed recording time
# DONE: show OBS recording time on stop recording (use GetRecordingStatus before stopping)
# DONE: show filename of current recording
# DONE: show OBS info on F1?
# DONE: Show available disk space
# DONE: warn on low disk space
# DONE: disable buttons when not valid

import asyncio
import simpleobsws
from tkinter import *
from tkinter import messagebox
import psutil
import subprocess
from datetime import timedelta
from os import getpid
from os.path import basename
from time import sleep
from vg_parm import VG_Parm

debug = False

parms = VG_Parm()

vr_version = '0.6'

# run-time variables
recording_in_progress = False
free_disk = 0.0
elapsed_time = 0
elapsed_time_after = None # where the callback for elapsed time is stored
obs_version = ''
obs_status = ''
ws_version = ''

async def get_obs_info( ):
    global parms, obs_version, ws_version, obs_status
    ##await ws.connect()
    info = await ws.call( 'GetVersion' )
    if debug: print( f'GetVersion: {info}')
    obs_version = info[ 'obs-studio-version' ]
    ws_version = info[ 'obs-websocket-version' ]
    obs_status = info[ 'status' ]
    await asyncio.sleep( 1 )
    ##await ws.disconnect()
    if debug: print( f'vr: {vr_version}, obs: {obs_version}, ws: {ws_version}, status: {obs_status}')

#async def get_obs_stats( ):
#    ##await ws.connect( )
#    stats = await ws.call( 'GetStats' )
#    if debug: print( f'GetStats: {stats}')
#    await asyncio.sleep( 1 )
#    ##await ws.disconnect( )
       
def show_disk_space( ):
    global free_disk
    vr.deiconify()
    free_disk = psutil.disk_usage('.').free / 1024 / 1024
    if free_disk < parms.free_disk_min:
        ds.config( bg = parms.text_warn_color )
    else:
        ds.config( bg = parms.bg_color )
    disk_space_text.set( f'Available disk space: {free_disk/1024:.1f}G ' )
    vr.after( parms.fd_delay, show_disk_space )

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
    show_app_status( 'Do NOT close OBS: the recording will fail', parms.text_warn_color )
    recording_in_progress = True
    loopy.run_until_complete( __start_recording( ) )
    show_recording_status( 'Recording', parms.text_warn_color )
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
    show_recording_status( 'Stopped', parms.text_info_color )
    show_app_status( f'File "{recording_filename.get()}" saved to the desktop', parms.text_done_color )
    btn_start[ 'state' ] = NORMAL


def show_recording_status( txt, color ): # Show status message next to buttons
    recording_state_label.config( fg = color )
    recording_state.set( txt )

def show_app_status( txt, color=parms.text_soft_color ):
    app_status.config( fg = color )
    app_status_text.set( txt )
    vr.update()

def show_elapsed_time():
    global recording_in_progress, elapsed_time, elapsed_time_after
    if debug: print( f'show_elapsed_time: {elapsed_time}')
    if recording_in_progress:
        recording_time.set( str( timedelta( seconds=elapsed_time ) ) )
        elapsed_time += 1
        elapsed_time_after = vr.after( 1000, show_elapsed_time )
    #else:
        #recording_time.set( '' )


def is_process_running(processName): # https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/
    ''' Check if there is any running process that contains the given name processName. '''
    for proc in psutil.process_iter(): #Iterate over the all the running processes
        try:
            if processName.lower() in proc.name().lower(): # Check if process name contains the given name string
                if debug: print( f'{processName} is running')
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            if debug: print( f'{processName} NOT running')
            return False
        except (psutil.ZombieProcess):
            # TODO: need to kill it
            return False

def start_obs( ):
    global parms
    show_app_status('Starting OBS', parms.text_info_color)
    try:
        rc = subprocess.Popen(parms.obs_command, cwd = parms.obs_directory)
        show_app_status('Waiting for OBS to be ready', parms.text_info_color)
        sleep(4) # 3 works, but barely; using 4 in case of a Blue Moon        
        if debug: print( f'Popen succeeded, returning {rc}')
        return True
    except:
        if debug: print( 'ERROR: OBS could not be started' ) 
        return False

def check_obs( ):
    global parms
    # if OBS isn't running, start it
    if not is_process_running( parms.obs_processname ):
        if( start_obs() ):
            show_app_status('OBS is running')
            return True
        else:
            btn_start[ 'state' ] = DISABLED
            btn_stop[ 'state' ] = DISABLED
            show_app_status( 'ERROR: OBS could not be started', parms.text_warn_color )
            return False
    else:
        show_app_status('OBS is running')
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

def is_running(script): #https://discuss.dizzycoding.com/check-to-see-if-python-script-is-running/
    for q in psutil.process_iter():
        if q.name().startswith('python'):
            if (len(q.cmdline())>1) and (script in q.cmdline()[1]) and (q.pid != getpid()):
                return True
    return False

def close_program():
    vr.deiconify()
    if recording_in_progress:
        if messagebox.askokcancel("Quit", "Do you want to quit? This will stop the recording."):
            stop_recording()
            vr.destroy()
    else:
        if messagebox.askokcancel("Quit", "Do you want to close the program?"):
            vr.destroy()

#---------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':

    # first, check if another instance is already running
    if is_running('videograbber'): #
        if debug: print('videograbber is already running')
        exit(1)

    # OK, we're in; build the window  
    vr = Tk()  
    # #vr.iconbitmap('VideoGrabberIcon.ico')
    vr.iconbitmap(default='VideoGrabberIcon.ico')
    vr.attributes( '-alpha', parms.bg_alpha ) # set transparency
    vr.attributes( '-topmost', 1 ) # force it to stay on top (so user doesn't lose it)
    vr.geometry(parms.vr_geometry)
    vr.resizable( False, False )
    vr.title(parms.vr_title)
    vr.wm_deiconify()
    vr.protocol("WM_DELETE_WINDOW", close_program)


    # frame for start button
    fr1 = Frame( master=vr, padx = 8, pady = 8 )
    fr1.grid( row=0, column=0, rowspan=3, padx = 4, pady = 4, sticky='wn' )

    # create 'start' button
    btn_start = Button( fr1, text = 'Record',
        height=parms.btn_height, width=parms.btn_width,
        command = start_recording,
        state=DISABLED,
        font = ( parms.font_bold, parms.btn_font_size ),
        fg=parms.text_warn_color
        )
    btn_start.grid( row=0, column=0 )

     # frame for stop
    fr2 = Frame( master=vr, padx = 8, pady = 8 )
    fr2.grid( row=0, column=1, rowspan=3, padx = 4, pady = 4, sticky='wn' )
   
    # create 'stop' button
    btn_stop = Button( fr2, text = 'Stop',
        height=parms.btn_height, width=parms.btn_width,
        command = stop_recording,
        state = DISABLED,
        font = ( parms.font_bold, parms.btn_font_size )
        )
    btn_stop.grid( row=0, column=0 )

    # frame/label for recording state, filename, time
    recording_state_frame = Frame( master=vr, padx=8, pady=8 )
    recording_state_frame.grid( row=0, column=2, padx=4, pady=4, sticky='wn')
    recording_state = StringVar()
    recording_state_label = Label( recording_state_frame, textvariable=recording_state, font=( parms.font_bold, parms.st_font_size ), anchor='w' )
    recording_state_label.grid( sticky='w' )

    # frame/label for output filename
    recording_filename = StringVar()
    recording_filename_label = Label( recording_state_frame, textvariable=recording_filename, font=( parms.font_family, parms.recording_filename_fontsize ), anchor='w' )
    recording_filename_label.grid( sticky='w')
    
    # frame/label for recording time
    recording_time = StringVar()
    recording_time_label = Label( recording_state_frame, textvariable=recording_time, font=( parms.font_family, parms.elapsed_time_fontsize ), anchor='w' )
    recording_time_label.grid( sticky='w' )

    # frame/label for disk space
    fr3 = Frame( master=vr, padx = 8, pady = 8 )
    fr3.grid( row = 3, column=0, columnspan=3, sticky='w' )
    disk_space_text = StringVar()
    ds = Label( fr3, textvariable=disk_space_text, font=( parms.font_family, parms.fd_font_size ), anchor='w' )
    ds.grid( sticky='w')
    ds.config( fg=parms.text_info_color )

    # frame/label for app status
    app_status_frame = Frame( master=vr, padx = 8, pady = 8 )
    app_status_frame.grid( row = 4, column=0, columnspan=3, sticky='w' )
    app_status_text = StringVar()
    app_status = Label( fr3, textvariable=app_status_text, font=( parms.font_bold, parms.app_status_font_size ), anchor='w' )
    app_status.grid( sticky='w' )

    info_line_frame = Frame( master=vr, padx = 8, pady = 8 )
    info_line_frame.grid( row = 5, column=0, columnspan=3, sticky='w' )
    info_line_text = StringVar()
    info_line = Label( info_line_frame, textvariable=info_line_text, font=( parms.font_italic, parms.info_line_font_size ) )
    info_line.grid( sticky='' )

    vr.update()

    loopy = asyncio.get_event_loop()
    # TODO: loopy = asyncio.new_event_loop()

    if( check_obs( ) ): # if OBS start ok, then we can proceed
        # set up an interface to OBS Studio
        ws = simpleobsws.obsws(host=parms.obs_host, port=parms.obs_port, password=parms.obs_pswd, loop=loopy)
        loopy.run_until_complete( ws.connect() )
        ws.register( on_obs_event )

        loopy.run_until_complete( get_obs_info( ) )
        info_line.config( fg=parms.text_soft_color)
        info_line_text.set( f'vr: {vr_version}, obs: {obs_version}, ws: {ws_version}, status: {obs_status}' )

        vr.update()

        show_disk_space() # schedules itself to re-run every fd_delay milliseconds (default one minute)

        btn_start['state'] = NORMAL
        
        if debug: print( 'all set; entering the tk mainloop' )
    else:
        show_app_status( 'ERROR: OBS could not be started. Restart me.', parms.text_warn_color)
        sleep( 8 )
        vr.destroy()
        exit( 17 )

    vr.mainloop()
