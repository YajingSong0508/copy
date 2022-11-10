
from os import path
import re
import sys
import threading
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory

import traceback
import time
import PySimpleGUI as sg

import plotter
import source_meter_gui as gui
import file_io as f
from plotter import plot_data
from calculations import calculate_params
import communication as comm
from sub_plots import plot_subplots

# reroute print statements to the Alerts Multiline element in the gui
print = gui.alert

default_profile = "./Keithley/default_profile.ini"
spec_file = './Keithley/profilespec.ini'
# define ranges and datatypes for the profile files

user_dir = ''

autosave = True
# auto save turn on from begining

# Use dictionary to store key1:value1, key2:value2... print['key'], we get value
# most recently measured/loaded data (forward+reverse scans)
data = {
    'voltages_forward': [],  # V
    'currents_forward': [],  # mA
    'current_densities_forward': [],  # mA/cm2

    'voltages_reverse': [],  # V
    'currents_reverse': [],  # mA
    'current_densities_reverse': [],  # mA/cm2
}


data2 = {
    'voltages_forward': [],  # V
    'currents_forward': [],  # mA
    'current_densities_forward': [],  # mA/cm2

    'voltages_reverse': [],  # V
    'currents_reverse': [],  # mA
    'current_densities_reverse': [],  # mA/cm2
}

# most recent test time
sweep_time = 0.0
volt_rate = 0.0
# set most recent test time
sweep_time2 = 0.0
volt_rate2 = 0.0
# most recent calculated values
results_forward = {}
results_reverse = {}
# to store most recent calculated values
results2_forward = {}
results2_reverse = {}


# thread handling Keithley communication
measure_thread = None
#The None keyword is used to define a null value, or no value at all. None is not the same as 0, False, or an empty string. None is a data type of its own (NoneType) and only None can be None.


def update_output():
    """
    Update the plot and recalculate and update the results.

    :return: nothing
    """
    global results_forward, results_reverse, values
    # these two variables can be use out of local function

    values = window.read(0)[1]
    plot_data(window, data, show_density=values['-CURR-DENSITY-'])

    try:
        results_forward = calculate_params(data['voltages_forward'], data['currents_forward'],
                                           float(values['-AREA-']), float(values['-ILLUM-']))
        results_reverse = calculate_params(data['voltages_reverse'], data['currents_reverse'],
                                           float(values['-AREA-']), float(values['-ILLUM-']))

        # todo: clean this up, put in sort_data or calculate_params?
        if results_forward and results_reverse:
            results_forward['sweep_time'] = results_reverse['sweep_time'] = (sweep_time / 2)
            results_forward['volt_rate'] = results_reverse['volt_rate'] = volt_rate
        elif results_forward:
            results_forward['sweep_time'] = sweep_time
            results_forward['volt_rate'] = volt_rate
        elif results_reverse:
            results_reverse['sweep_time'] = sweep_time
            results_reverse['volt_rate'] = volt_rate


    except:
        print('Calculations failed - go bug Ajan', c=gui.ERROR)
        print(traceback.format_exc(), c=gui.ERROR)

    gui.display_results(results_forward, results_reverse)


def threaded_IV():
    """
    Run an IV test and update the data dictionary. Performs all the communication with the Keithley.
    Supposed to be run as a separate thread.

    :return: nothing
    """
    global data, sweep_time, volt_rate
    params = gui.read_profile()

    # this variable is monitored during the IV test and will be set to True if the user wants to cancel the test
    # works across files and threads
    comm.cancel_measure = False
    try:
        voltages, currents, sweep_time, volt_rate = comm.run_IV_test(src_meter, params)
    except:
        print('Unhandled exception when running test - please report', c=gui.ERROR)
        print(traceback.format_exc(), c=gui.ERROR)
        voltages = []
        currents = []

    current_densities = [curr / params['area'] for curr in currents]

    # use file loading sort to split data from source meter
    data = f.sort_data(voltages, [], currents, [], current_densities, [])
    # notify main thread the test is complete
    window.write_event_value('-TEST-COMPLETE-', '')


def timer( ):
    global data, sweep_time, volt_rate,x_time,y_PCE
    global results_forward2, results_reverse2, values

    comm.cancel_measure = False
    duration = 0.02  # hour
    comm.connect_to_instrument()
    x_time=[] # define a y_time list to stor the time point
    y_PCE=[]
    while (time.time() - start_time) / 3600 <= duration:
        params = gui.read_profile2()

        voltages, currents, sweep_time, volt_rate = comm.run_IV_test(src_meter, params)


        current_densities = [curr / params['area'] for curr in currents]

        # use file loading sort to split data from source meter
        data = f.sort_data(voltages, [], currents, [], current_densities, [])


        results_forward2 = calculate_params(data['voltages_forward'], data['currents_forward'], float(values['-AREA-']),
                                          float(values['-ILLUM-']))

        time_point = (time.time() - start_time) / 3600
        PCE = results_forward2['PCE']
        x_time.append(time_point)
        y_PCE.append(PCE)
        if comm.cancel_measure ==True:
            break

    else:
        window.write_event_value('-test-complete-', '')

    return x_time, y_PCE



def update_output2():
            global results_forward2, results_reverse2, values
            global x_time, y_PCE
            values = window.read(0)[1]
            plot_subplots(window,x_time,y_PCE)





# load GUI
window = gui.init_gui()
if window is None:
    print("GUI init error")
    sys.exit(1)

# if on small lab laptop - start app fullscreen
# to simulate this when developing, set resolution of laptop screen to 1366x768
if sg.Window.get_screen_size()[0] < 1500:
    window.maximize()



print('Session started')


# close the splash screen if launched from exe
try:
    import pyi_splash

    pyi_splash.close()
except ModuleNotFoundError:
    pass

f.load_profile(default_profile, spec_file, window)


while True:
    event, values = window.read()

    #output_key = "-ALERTS-" # new
    #window['-OUT-'].update(f'{event, values}')
    #global MLINE_KEY, MLINE_KEY2, output_key

    #MLINE_KEY = '-ML-' + sg.WRITE_ONLY_KEY  # multiline element's key. Indicate it's an output only element
    #MLINE_KEY2 = '-ML2-' + sg.WRITE_ONLY_KEY

    #output_key = MLINE_KEY

    #sg.cprint_set_output_destination(window, output_key)

    ########################################
    if event == '-CURR-DENSITY-':
        # toggle between plotting the current or the current density
        plot_data(window, data, show_density=values['-CURR-DENSITY-'])

    if event in ('Load Profile', '-LOAD-PROFILE-'):
        profile_path = askopenfilename(title='Open profile',
                                       filetypes=(('CONFIG', '.ini'),), defaultextension='.ini')
        f.load_profile(profile_path, spec_file, window)
        # todo: should loading a new profile update the results?

    if event in ('Save Profile', '-SAVE-PROFILE-'):


        profile_path = asksaveasfilename(title='Save profile',
                                         filetypes=(('CONFIG', '.ini'),), defaultextension='.ini')
        f.save_profile(profile_path, spec_file, gui.read_profile())

    if event in ('Load Data', '-LOAD-DATA-'):
        file_path = askopenfilename(title='Open data file',
                                    filetypes=(('CSV', '.csv'),), defaultextension='.csv')
        if not file_path:
            continue

        load_data = f.load_data(file_path)
        if not load_data:
            continue

        data = load_data
        # todo: recovering sweep time and volt rate from loaded data
        sweep_time = volt_rate = 0
        print('Confirm profile matches loaded data. If not, correct and reload', c=gui.WARNING)
        update_output()

    if event in ('Save Data', '-SAVE-DATA-'):
        device_name, experiment_name = gui.read_file_info()
        if not user_dir:
            gui.alert('Select User Directory before saving data', c=gui.ERROR)
            continue
        if not device_name:
            gui.alert('Enter Device Name before saving data', c=gui.ERROR)
            continue
        if not experiment_name:
            print('Enter Experiment Name before saving data', c=gui.ERROR)
            continue

        data_path, results_path = f.get_file_paths(user_dir, device_name, experiment_name)

        f.save_data(data_path, data)
        # todo: profile may have been edited since loading/measuring data - should save 'old' profile?
        #       this behaviour is communicated to users via the Keithley User Manual
        f.save_results(results_path, experiment_name, results_forward, results_reverse, gui.read_profile())

    if event in ('Start', '-START-MEASURE-'):
        #output_key = MLINE_KEY if output_key == MLINE_KEY2 else MLINE_KEY
        #sg.cprint_set_output_destination(window, output_key)

        src_meter = comm.connect_to_instrument()

        if not src_meter:
            continue
        if not comm.test_communication(src_meter):
            continue
        # grey out and disable sections of gui during tests
        gui.disable_profile(True)
        plotter.disable()
        # run IV test in separate thread
        thread1 = threading.Thread(target=threaded_IV)
        thread1.start()

    if event == '-TEST-COMPLETE-':
        thread1.join(10)
        if thread1.is_alive():
            print('Error joining test thread - Please report this', c=gui.ERROR)
        gui.disable_profile(False)
        plotter.enable()
        update_output()
        if autosave:
            window.write_event_value('-SAVE-DATA-', '')

    if event in ('Cancel', '-CANCEL-'):
        comm.cancel_measure = True

    if event == 'Choose Spec File':
        # todo: validate spec file (ie can't load profile as spec)
        spec_file_path = askopenfilename(title='Open Spec File',
                                         filetypes=(('CONFIG', '.ini'),), defaultextension='.ini')
        if spec_file_path:
            spec_file = spec_file_path
            print('Loaded spec file: ' + path.basename(spec_file))

    if event == '-CHOOSE-USER-':
        directory_path = askdirectory(title='Select Your Folder')
        if not directory_path:
            continue

        # find the date folder and take the parent (if no date folder, assume they picked the user top level folder)
        # using regex means this will work even if user picked a subfolder from a different date
        # todo: will break if there is not a date folder but there is a date/time somewhere else in the path
        user_dir = re.split('\d+-\d+-\d+', directory_path, maxsplit=1)[0]

        window['-USER-DIRECTORY-'].update(user_dir)
        print('Updated user directory to: ', path.basename(path.normpath(user_dir)))

    if event == 'Toggle Autosave':
        autosave = not autosave
        if autosave:
            window['-AUTOSAVE-'].update('AUTOSAVE ENABLED', background_color='green')
            print('Autosave enabled')
        else:
            window['-AUTOSAVE-'].update('AUTOSAVE DISABLED', background_color='red3')
            print('Autosave disabled')

    if event in (sg.WIN_CLOSED, 'Exit'):
        break

    # SECOND TAB FUNCTION starts here:##############

    if event in ('Start', '-start-measure-'):
        global start_time
        start_time = time.time()
        #output_key = MLINE_KEY2 if output_key == MLINE_KEY else MLINE_KEY2
        #sg.cprint_set_output_destination(window, output_key)
        src_meter = comm.connect_to_instrument()
        if not src_meter:
            continue
        if not comm.test_communication(src_meter):
            continue
        # grey out and disable sections of gui during tests
            # run IV test in separate thread
        thread2 = threading.Thread(target=timer)
        #thread3= threading.Thread(Target=update_output2())
        thread2.start()
        ##thread3.start()
    if event == '-test-complete-':
        thread2.join(10)
        #thread3.join(10)
        update_output2()
        if thread2.is_alive():
            print('Error joining test thread - Please report this', c=gui.ERROR)




    if event in ('Cancel', '-cancel-'):
        comm.cancel_measure = True

    if event == '-choose-user-':
        directory_path = askdirectory(title='Select Your Folder')
        if not directory_path:
            continue

        user_dir = re.split('\d+-\d+-\d+', directory_path, maxsplit=1)[0]

        window['-user-directory-'].update(user_dir)
        print('Updated user directory to: ', path.basename(path.normpath(user_dir)))


    if event in ('Load Profile', '-load-profile-'):
        profile_path = askopenfilename(title='Open profile',
                                       filetypes=(('CONFIG', '.ini'),), defaultextension='.ini')
        f.load_profile(profile_path, spec_file, window)
        # todo: should loading a new profile update the results?

    if event in ('Save Profile', '-save-profile-'):
        #output_key = MLINE_KEY2 if output_key == MLINE_KEY else MLINE_KEY
        #sg.cprint_set_output_destination(window, output_key)
        print('Switched to this output element', c='white on red')

        profile_path = asksaveasfilename(title='Save profile',
                                         filetypes=(('CONFIG', '.ini'),), defaultextension='.ini')
        f.save_profile(profile_path, spec_file, gui.read_profile())

    if event in ('Load Data', '-load-data-'):
        file_path = askopenfilename(title='Open data file',
                                    filetypes=(('CSV', '.csv'),), defaultextension='.csv')
        if not file_path:
            continue

        load_data = f.load_data(file_path)
        if not load_data:
            continue

        data = load_data
        # todo: recovering sweep time and volt rate from loaded data
        sweep_time = volt_rate = 0
        print('Confirm profile matches loaded data. If not, correct and reload', c=gui.WARNING)
        update_output()

    if event in ('Save Data', '-save-data-'):
        device_name, experiment_name = gui.read_file_info()
        if not user_dir:
            gui.alert('Select User Directory before saving data', c=gui.ERROR)
            continue
        if not device_name:
            gui.alert('Enter Device Name before saving data', c=gui.ERROR)
            continue
        if not experiment_name:
            print('Enter Experiment Name before saving data', c=gui.ERROR)
            continue

        data_path, results_path = f.get_file_paths(user_dir, device_name, experiment_name)

        f.save_data(data_path, data)
        # todo: profile may have been edited since loading/measuring data - should save 'old' profile?
        #       this behaviour is communicated to users via the Keithley User Manual
        f.save_results(results_path, experiment_name, results_forward, results_reverse, gui.read_profile())


window.close()  # destroy GUI window

sys.exit(0)  # exit program safely
