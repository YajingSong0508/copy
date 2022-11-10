
from datetime import datetime
from os import path

import PySimpleGUI as sg
from PySimpleGUI import Push

logo_path = './logos/logo.png'
icon_path = './logos/logo.ico'
# ensure found correctly from executable
logo_path = path.abspath(path.join(path.dirname(__file__), logo_path))
icon_path = path.abspath(path.join(path.dirname(__file__), icon_path))

font_small = 'Helvetica 10'
font_large = 'Helvetica 12'

# set to 1 to make frames visible (good for development), set to 0 to make invisible
bw = 0

# (w, h) w=characters-wide, h=rows-high. Minimum. If an int instead of a tuple is supplied, then height is auto-set to 1
text_size_long = 19
text_size_short = 15
input_size_number = 15
input_size_text = 20
button_size = 0
checkbox_size = 15
statusbar_size_number = 7
statusbar_size_text = 20

# (w, h) in pixels. Minimum. Can be expanded beyond this by included elements or with expand_x and expand_y
canvas_size = (600, 500)
results_size = (400, 500)

# (left/right, top/bottom) or ((left, right), (top, bottom)) in pixels
text_pad = (0, 2)
input_pad = (0, 0)
button_pad_center = (0, 4)
button_pad_left = ((3, 0), 4)
button_pad_right = ((0, 3), 4)
checkbox_pad = (0, 0)
logo_pad = ((0, 0), (5, 5))

# todo: list or no list for current limit
# oscilla does 0.02, 0.2, 2, 20, 150, we could do 0.02, 0.2, 2, 20, 200, 2000, 3000? limit is 3.15A
# oscilla does drop down list because it changes the ADC settings depending on the current limit
# keithley does not have that limitation

# alert colors
INFO = 'black'
COMPLETE = 'green'
IMPORTANT = 'blue'
WARNING = 'gold4'
ERROR = 'red2'

window = None


def alert(*args, **kwargs):
    """
    Print to Alerts Multiline element with timestamp

    :param args: positional arguments for sg.cprint()
    :param kwargs: keyword arguments for sg.cprint() (like colour)
    """
    sg.cprint(datetime.now().strftime("%X: "), end='')
    sg.cprint(*args, **kwargs)



# reroute print statements to the Alerts Multiline element in the gui
print = alert


# wrapper functions to make init_gui() less busy
def text_long(text, **kwargs):
    return sg.Text(text, font=font_small, pad=text_pad, size=text_size_long, **kwargs)


def text_short(text, **kwargs):
    return sg.Text(text, font=font_small, pad=text_pad, size=text_size_short, justification='left', **kwargs)


def button(text, pad=button_pad_center, **kwargs):
    return sg.Button(text, font=font_small, pad=pad, size=button_size, expand_x=True, **kwargs)


def input_number(**kwargs):
    return sg.Input(font=font_large, pad=input_pad, size=input_size_number, expand_x=True, **kwargs)


def input_text(**kwargs):
    return sg.Input(font=font_small, pad=input_pad, size=input_size_text, expand_x=True, **kwargs)


def statusbar_number(**kwargs):
    return sg.StatusBar(text='', font=font_large, pad=input_pad, size=statusbar_size_number, **kwargs)


def statusbar_text(**kwargs):
    return sg.StatusBar(text='', font=font_small, pad=input_pad, size=statusbar_size_text, **kwargs)


def checkbox(**kwargs):
    return sg.Checkbox('', pad=checkbox_pad, size=checkbox_size, enable_events=True, expand_x=True, **kwargs)


def init_gui():
    """
    Generate the GUI for the source meter app

    :return: sg.Window object
    """
    global window

    sg.theme("SystemDefault")

    menu_def = [['Config', ['Choose Spec File', 'Toggle Autosave']]]

    profile_frame = sg.Frame('', [[text_long('Device Area (cm2)'), Push(), input_number(key='-AREA-')],
                                  [text_long('Current Limit (mA)'), Push(), input_number(key='-CURR-LIMIT-')],
                                  [text_long('Start Voltage (V)'), Push(), input_number(key='-START-VOLT-')],
                                  [text_long('Stop Voltage (V)'), Push(), input_number(key='-STOP-VOLT-')],
                                  [text_long('Voltage Step (V)'), Push(), input_number(key='-VOLT-STEP-')],
                                  [text_long('Voltage Settle Time (s)'), Push(), input_number(key='-SETTLE-TIME-')],
                                  [text_long('Illumination (mW/cm2)'), Push(), input_number(key='-ILLUM-')],
                                  [text_long('Hysteresis'), Push(), checkbox(key='-HYSTERESIS-')],
                                  [text_long('Current Density (mA/cm2)'), Push(), checkbox(key='-CURR-DENSITY-')]],
                             border_width=bw, expand_x=True, pad=(0, 0))

    profile_frame2 = sg.Frame('', [[text_long('Device Area (cm2)'), Push(), input_number(key='-area-')],
                                  [text_long('Current Limit (mA)'), Push(), input_number(key='-current-limit-')],
                                  [ text_long('Samples per point'), Push(), input_number(key='-samples-per-point-')],
                                  [text_long('Start Voltage (V)'), Push(), input_number(key='-start-volt')],
                                  [text_long('Stop Voltage (V)'), Push(), input_number(key='-stop-volt-')],
                                  [text_long('Voltage Step (V)'), Push(), input_number(key='-voltage-step-')],
                                  [text_long('Voltage Settle Time (s)'), Push(), input_number(key='-settle-time-')],
                                  [text_long('Illumination (mW/cm2)'), Push(), input_number(key='-illum-')],
                                  [text_long('Hysteresis'), Push(), checkbox(key='-hysteresis-')],
                                  [text_long('')],
                                  [text_long('Duration (Hours)'), Push(), input_number(key='-duar')]],

                             border_width=bw, expand_x=True, pad=(0, 0))

    button_frame = sg.Frame('', [[button('Load Profile', key='-LOAD-PROFILE-', pad=button_pad_right),
                                  button('Save Profile', key='-SAVE-PROFILE-', pad=button_pad_left)],
                                 [button('Load Data', key='-LOAD-DATA-')],
                                 [button('Start Measurement', key='-START-MEASURE-', button_color='green')],
                                 [button('Cancel', key='-CANCEL-', button_color='red3')]],
                            border_width=bw, expand_x=True, pad=(0, 0))

    button_frame2 = sg.Frame('', [[button('Load Profile', key='-load-profile-', pad=button_pad_right),
                                  button('Save Profile', key='-save-profile-', pad=button_pad_left)],
                                 [button('Load Data', key='-load-data-')],
                                  [button('Toggle')],
                                 [button('Start Measurement', key='-start-measure-', button_color='green')],
                                 [button('Cancel', key='-cancel-', button_color='red3')]],
                            border_width=bw, expand_x=True, pad=(0, 0))

    results_frame = sg.Frame('', [[Push(), text_long('  ', key='-LABELS-')],
                                  [text_long('J_sc (mA/cm2)'), Push(), statusbar_number(key='-J_SC-'),
                                   statusbar_number(key='-J_SC-R-', visible=False)],
                                  [text_long('V_oc (V)'), Push(), statusbar_number(key='-V_OC-'),
                                   statusbar_number(key='-V_OC-R-', visible=False)],
                                  [text_long('R_shunt (Ω)'), Push(), statusbar_number(key='-R_SH-'),
                                   statusbar_number(key='-R_SH-R-', visible=False)],
                                  [text_long('R_series (Ω)'), Push(), statusbar_number(key='-R_S-'),
                                   statusbar_number(key='-R_S-R-', visible=False)],
                                  [text_long('Max power (mW/cm2)'), Push(), statusbar_number(key='-MAX-POWER-'),
                                   statusbar_number(key='-MAX-POWER-R-', visible=False)],
                                  [text_long('V_mpp (V)'), Push(), statusbar_number(key='-V_MPP-'),
                                   statusbar_number(key='-V_MPP-R-', visible=False)],
                                  [text_long('I_mpp (mA/cm2)'), Push(), statusbar_number(key='-I_MPP-'),
                                   statusbar_number(key='-I_MPP-R-', visible=False)],
                                  [text_long('PCE (%)'), Push(), statusbar_number(key='-PCE-'),
                                   statusbar_number(key='-PCE-R-', visible=False)],
                                  [text_long('Fill factor (%)'), Push(), statusbar_number(key='-FF-'),
                                   statusbar_number(key='-FF-R-', visible=False)],
                                  [text_long('Sweep Time (s)'), Push(), statusbar_number(key='-ST-'),
                                   statusbar_number(key='-ST-R-', visible=False)],
                                  [text_long('Voltage rate (V/s)'), Push(), statusbar_number(key='-V_R-'),
                                   statusbar_number(key='-V_R-R-', visible=False)]],
                             border_width=bw, expand_x=True, pad=(0, 0))

    graph_frame = sg.Frame('', [[sg.Canvas(key='-GRAPH-CONTROLS-', expand_x=True)],
                                [sg.Canvas(key='-GRAPH-', expand_x=True, expand_y=True)]], size=canvas_size,
                           border_width=bw, expand_x=True, expand_y=True, pad=(0, 0), element_justification='center')

    graph_frame2 = sg.Frame('', [[sg.Canvas(key='-graph-controls-', expand_x=True)],
                                [sg.Canvas(key='-graph-', expand_x=True, expand_y=True)]], size=canvas_size,
                           border_width=bw, expand_x=True, expand_y=True, pad=(0, 0), element_justification='center')

    naming_frame = sg.Frame('', [[text_short('User Directory'),
                                  statusbar_text(justification='right', key='-USER-DIRECTORY-')],
                                 [text_short('Experiment Name'), input_text(key='-EXPERIMENT-NAME-')],
                                 [text_short('Device Name'), input_text(key='-DEVICE-NAME-')],
                                 [button('Choose User Directory', key='-CHOOSE-USER-', pad=button_pad_right),
                                  button('Save Data', key='-SAVE-DATA-', pad=button_pad_left)],
                                 [text_long('AUTOSAVE ENABLED', key='-AUTOSAVE-', text_color='white',
                                            background_color='green',
                                            justification='center')]],
                            border_width=bw, expand_x=True, element_justification='right', pad=(0, 0))

    naming_frame2 = sg.Frame('', [[text_short('User Directory'),
                                  statusbar_text(justification='right', key='-user-directory-')],
                                 [text_short('Experiment Name'), input_text(key='-experiment-name-')],
                                 [text_short('Device Name'), input_text(key='-device-name-')],
                                 [button('Choose User Directory', key='-choose-user-', pad=button_pad_right),
                                  button('Save Data', key='-save-data-', pad=button_pad_left)],
                                 [text_long('AUTOSAVE ENABLED', key='-autosave-', text_color='white',
                                            background_color='green',
                                            justification='center')]],
                            border_width=bw, expand_x=True, element_justification='right', pad=(0, 0))

    #global  MLINE_KEY,MLINE_KEY2,output_key

    MLINE_KEY = '-ML-' + sg.WRITE_ONLY_KEY  # multiline element's key. Indicate it's an output only element
    MLINE_KEY2 = '-ML2-' + sg.WRITE_ONLY_KEY  # multiline element's key. Indicate it's an output only element


    #output_key = MLINE_KEY

    #sg.cprint_set_output_destination(window, output_key)  # delete





    alert_frame2 = sg.Frame('', [[sg.Multiline("report window 2 \n", expand_x=True, expand_y=True, key= MLINE_KEY2
                                               ,reroute_cprint=True, autoscroll=True,
                                             write_only=True, auto_refresh=True, pad=(0, 0))]],
                          border_width=bw, expand_x=True, expand_y=True, pad=(0, 4))



    alert_frame = sg.Frame('', [[sg.Multiline("report window 1\n", expand_x=True, expand_y=True, key= MLINE_KEY,
                                              reroute_cprint=True, autoscroll=True,
                                              write_only=True, auto_refresh=True, pad=(0, 0))]],
                           border_width=bw, expand_x=True, expand_y=True, pad=(0, 4))


    logo_frame = sg.Frame('', [[sg.Image(logo_path, pad=logo_pad)]],
                          border_width=bw, element_justification='right', vertical_alignment='bottom', pad=(0, 0))

    logo_frame2 = sg.Frame('', [[sg.Image(logo_path, pad=logo_pad)]],
                          border_width=bw, element_justification='right', vertical_alignment='bottom', pad=(0, 0))

    # todo: make input col not expand when window maximized - make profile_frame limit width
    # this may be a fundamental limitation with PySimpleGUI, haven't been able to get just two cols to expand
    # the Column element technically doesn't expand, but gets centered in extra empty space
    input_col = sg.Column([[profile_frame], [sg.VPush()], [button_frame], [sg.VPush()], [results_frame]],
                          vertical_alignment='top', expand_y=True, expand_x=True, element_justification='left')

    input_col2 = sg.Column([[profile_frame2], [sg.VPush()], [button_frame2], [sg.VPush()]],
                          vertical_alignment='top', expand_y=True, expand_x=True, element_justification='left')

    graph_col = sg.Column([[graph_frame]], expand_y=True, expand_x=True, element_justification='center')

    graph_col2 = sg.Column([[graph_frame2]], expand_y=True, expand_x=True, element_justification='center')

    alert_col = sg.Column([[naming_frame], [alert_frame], [logo_frame]], expand_y=True, expand_x=True,
                          element_justification='right')
    alert_col2 = sg.Column([[naming_frame2],[alert_frame2],[logo_frame2]], expand_y=True, expand_x=True,
                          element_justification='right')

    char_layout = [[sg.Menu(menu_def)], [input_col, graph_col, alert_col]]
    lifetime_layout = [[input_col2, graph_col2, alert_col2]]

    layout = [
        [sg.TabGroup([[sg.Tab("Solar Cell Characterisation", char_layout, tooltip='tip'), sg.Tab('Solar Lifetime Measurement', lifetime_layout, key='-Solar Lifetime Measurement-')]])],
    ]
    window = sg.Window('Rayleigh Keithley Source Meter App',layout, icon=icon_path, resizable=True, finalize=True,
                       margins=(0, 0), element_justification='left')



    return window



def read_profile():
    assert isinstance(window, sg.Window)  # asserts in these functions to disable warnings about window being None
    values = window.read(0)[1]
    profile = None
    try:
        profile = {'area': float(values['-AREA-']),
                   'curr_limit': float(values['-CURR-LIMIT-']),
                   'start_volt': float(values['-START-VOLT-']),
                   'stop_volt': float(values['-STOP-VOLT-']),
                   'volt_step': float(values['-VOLT-STEP-']),
                   'settle_time': float(values['-SETTLE-TIME-']),
                   'illum': float(values['-ILLUM-']),
                   'hysteresis': values['-HYSTERESIS-'],
                   'curr_density': values['-CURR-DENSITY-']}
    except ValueError:
        print('Invalid value in profile', c=ERROR)
    else:
        if abs(profile['start_volt'] - profile['stop_volt']) < abs(profile['volt_step']):
            print('Volt Step bigger than volt range', c=WARNING)

    return profile


def read_profile2():
    assert isinstance(window, sg.Window)  # asserts in these functions to disable warnings about window being None
    values = window.read(0)[1]
    profile = None
    try:
        profile = {'area': float(values['-area-']),
                   'curr_limit': float(values['-curr-limit-']),
                   'start_volt': float(values['-start-volt-']),
                   'stop_volt': float(values['-stop-volt-']),
                   'volt_step': float(values['-volt-step-']),
                   'settle_time': float(values['-settle-time-']),
                   'illum': float(values['-illum-']),
                   'hysteresis': values['-hysteresis-'],
                   'curr_density': values['-curr-density-']}
    except ValueError:
        print('Invalid value in profile', c=ERROR)
    else:
        if abs(profile['start_volt'] - profile['stop_volt']) < abs(profile['volt_step']):
            print('Volt Step bigger than volt range', c=WARNING)

    return profile


def disable_profile(disabled: bool):
    assert isinstance(window, sg.Window)
    window['-START-MEASURE-'].update(disabled=disabled)
    window['-LOAD-PROFILE-'].update(disabled=disabled)
    window['-LOAD-DATA-'].update(disabled=disabled)
    window['-AREA-'].update(disabled=disabled)
    window['-CURR-LIMIT-'].update(disabled=disabled)
    window['-START-VOLT-'].update(disabled=disabled)
    window['-STOP-VOLT-'].update(disabled=disabled)
    window['-VOLT-STEP-'].update(disabled=disabled)
    window['-SETTLE-TIME-'].update(disabled=disabled)
    window['-ILLUM-'].update(disabled=disabled)
    window['-HYSTERESIS-'].update(disabled=disabled)
    window['-CURR-DENSITY-'].update(disabled=disabled)



def display_results(results_forward: dict, results_reverse: dict):
    assert isinstance(window, sg.Window)
    if not (results_forward or results_reverse):
        return
    precision = 2

    change_results_visibility(bool(results_forward), bool(results_reverse))

    if results_forward:
        window['-J_SC-'].update(round(results_forward['J_sc'], precision))
        window['-V_OC-'].update(round(results_forward['V_oc'], precision))
        window['-R_SH-'].update(round(results_forward['R_sh'], precision))
        window['-R_S-'].update(round(results_forward['R_s'], precision))
        window['-MAX-POWER-'].update(round(results_forward['max_power'], precision))
        window['-V_MPP-'].update(round(results_forward['V_mpp'], precision))
        window['-I_MPP-'].update(round(results_forward['I_mpp'], precision))
        window['-PCE-'].update(round(results_forward['PCE'], precision))
        window['-FF-'].update(round(results_forward['FF'], precision))
        window['-ST-'].update(round(results_forward['sweep_time'], precision + 1))
        window['-V_R-'].update(round(results_forward['volt_rate'], precision + 1))
    if results_reverse:
        window['-J_SC-R-'].update(round(results_reverse['J_sc'], precision))
        window['-V_OC-R-'].update(round(results_reverse['V_oc'], precision))
        window['-R_SH-R-'].update(round(results_reverse['R_sh'], precision))
        window['-R_S-R-'].update(round(results_reverse['R_s'], precision))
        window['-MAX-POWER-R-'].update(round(results_reverse['max_power'], precision))
        window['-V_MPP-R-'].update(round(results_reverse['V_mpp'], precision))
        window['-I_MPP-R-'].update(round(results_reverse['I_mpp'], precision))
        window['-PCE-R-'].update(round(results_reverse['PCE'], precision))
        window['-FF-R-'].update(round(results_reverse['FF'], precision))
        window['-ST-R-'].update(round(results_reverse['sweep_time'], precision + 1))
        window['-V_R-R-'].update(round(results_reverse['volt_rate'], precision + 1))


def change_results_visibility(show_forward: bool, show_reverse: bool):
    assert isinstance(window, sg.Window)

    # todo: line up labels with cols of results for both normal and maximized views
    window['-LABELS-'].update('Forward         Reverse' if (show_forward and show_reverse) else '  ')

    window['-J_SC-'].update(visible=show_forward)
    window['-V_OC-'].update(visible=show_forward)
    window['-R_SH-'].update(visible=show_forward)
    window['-R_S-'].update(visible=show_forward)
    window['-MAX-POWER-'].update(visible=show_forward)
    window['-V_MPP-'].update(visible=show_forward)
    window['-I_MPP-'].update(visible=show_forward)
    window['-PCE-'].update(visible=show_forward)
    window['-FF-'].update(visible=show_forward)
    window['-ST-'].update(visible=show_forward)
    window['-V_R-'].update(visible=show_forward)

    window['-J_SC-R-'].update(visible=show_reverse)
    window['-V_OC-R-'].update(visible=show_reverse)
    window['-R_SH-R-'].update(visible=show_reverse)
    window['-R_S-R-'].update(visible=show_reverse)
    window['-MAX-POWER-R-'].update(visible=show_reverse)
    window['-V_MPP-R-'].update(visible=show_reverse)
    window['-I_MPP-R-'].update(visible=show_reverse)
    window['-PCE-R-'].update(visible=show_reverse)
    window['-FF-R-'].update(visible=show_reverse)
    window['-ST-R-'].update(visible=show_reverse)
    window['-V_R-R-'].update(visible=show_reverse)


def read_file_info():
    assert isinstance(window, sg.Window)
    values = window.read(0)[1]

    device_name = values['-DEVICE-NAME-'].strip()
    experiment_name = values['-EXPERIMENT-NAME-'].strip()

    return device_name, experiment_name
