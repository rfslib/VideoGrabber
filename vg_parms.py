
VG_Parms = {
    # control window attributes
    'icon' : 'VideoGrabberIcon.ico',
    'vr_title' : 'Riverton FamilySearch Library Video Grabber',
    'vr_geometry' : '500x220+72+32',
    'bg_color' : 'SystemButtonFace',
    'bg_alpha' : 0.95,
    'text_info_color' : 'Black',
    'text_warn_color' : 'Red',
    'text_done_color' : 'DarkGreen',
    'text_soft_color' : 'Grey',
    'font_family' : 'Consolas',
    'font_bold' : 'Consolas Bold',
    'font_italic' : 'Consolas Italic',

    'btn_font_size' : 16,
    'btn_height' : 3,
    'btn_width' : 8,
    'st_font_size' : 16, # recording status ('Recording' or 'Stopped')
    'recording_filename_fontsize' : 11,
    'elapsed_time_fontsize' : 11,
    'free_disk_min' : 5000.0, # minimum available space on disk before displaying warning
    'fd_font_size' : 12,
    'fd_delay' : 60000,  # 60000 to update available disk space once a minute
    'app_status_font_size' : 12,
    'info_line_font_size' : 8,

    # OBS
    'obs_processname' : 'obs64.exe',
    'obs_command' : r'C:\Program Files\obs-studio\bin\64bit\obs64.exe',
    'obs_directory' : r'C:\Program Files\obs-studio\bin\64bit',
    'obs_startup_parms' : '--disable-updater', # was r'--always-on-top'

    # OBS interface
    'obs_pswd' : 'family',
    'obs_host' : '127.0.0.1',
    'obs_port' : 4444,

    # expected (tested) versions
    'expected_obs_version' : '27.2.4',
    'expected_ws_version' : '4.9.1',
    'expected_simpleobsws_version' : '1.1',

    # ignap
    'snark' : 'whatever'
}
