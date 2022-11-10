# -*- coding: utf-8 -*-
"""
Rayleigh Solar Tech

Source Meter UI project
file_io.py

Functions for loading and writing data to files

Created on: July 15th, 2022
Created by: Seamus MacInnes

Updated on: August 19th, 2022
Updated by: Seamus MacInnes

lastest update: Oct 17th, 2022
updated by : Yajing Song
"""

import os
from datetime import datetime

import PySimpleGUI
from configobj import ConfigObj
from pandas import read_csv, DataFrame, concat, to_numeric
from validate import Validator
import source_meter_gui as gui
from contextlib import contextmanager

# reroute print statements to the Alerts Multiline element in the gui
print = gui.alert

file_op_errors = False  # flag for most recent file operation


def get_file_paths(user_directory: str, device_name: str, experiment_name: str) -> (str, str):
    """
    Create file paths for the data file and the results/profile file

    data file path is <user>/<date>/<device>/data/<date> <time> <device> <experiment> data.csv

    results file path is <user>/<date>/<device>/<date> <device> results.csv

    :param user_directory: Path to current user's directory
    :param device_name: Name of device being tested
    :param experiment_name: Name for experiment being performed
    :return: data path and results path
    """
    if not user_directory or not device_name or not experiment_name:
        return None, None

    date = datetime.now().strftime('%Y-%m-%d')
    time = datetime.now().strftime('%H-%M-%S')

    core_path = os.path.join(user_directory, date, device_name)

    data_filename = ' '.join([date, time, device_name, experiment_name, 'data.csv'])
    results_filename = ' '.join([date, device_name, 'results.csv'])

    data_path = os.path.abspath(os.path.join(core_path, 'data', data_filename))
    results_path = os.path.abspath(os.path.join(core_path, results_filename))

    return data_path, results_path


def sort_data(voltages_1: list, voltages_2: list, currents_1: list, currents_2: list, current_densities_1: list,
              current_densities_2: list) -> dict:
    """
    Analyze the file/keithley data so forward/reverse scans are sorted properly
    If there are two scans (same col or not) they are assumed to have the same number of data points

    data format options:
    col1: forward
    col1: reverse
    col1: forward-reverse
    col1: reverse-forward
    col1: forward col2: reverse
    col1: reverse col2: forward

    :param voltages_1: first col of voltages
    :param voltages_2: second col of voltages
    :param currents_1: first col of currents
    :param currents_2: second col of currents
    :param current_densities_1: first col of current densities
    :param current_densities_2: second col of current densities
    :return: a data dictionary where forward and reverse scans are properly sorted
    """

    is_two_cols = bool(voltages_2)
    if len(voltages_1) < 2:
        col1_is_forward = True
        col1_is_two_scans = False
    else:
        col1_is_forward = (voltages_1[1] > voltages_1[0])  # increasing slope at start
        col1_is_two_scans = (col1_is_forward != (voltages_1[-1] > voltages_1[-2]))  # start slope != end slope

    data = {}

    if is_two_cols:
        if col1_is_forward:
            data['voltages_forward'] = voltages_1
            data['currents_forward'] = currents_1
            data['current_densities_forward'] = current_densities_1
            data['voltages_reverse'] = voltages_2
            data['currents_reverse'] = currents_2
            data['current_densities_reverse'] = current_densities_2
        else:
            data['voltages_forward'] = voltages_2
            data['currents_forward'] = currents_2
            data['current_densities_forward'] = current_densities_2
            data['voltages_reverse'] = voltages_1
            data['currents_reverse'] = currents_1
            data['current_densities_reverse'] = current_densities_1
    elif col1_is_two_scans:
        mid = int(len(voltages_1) / 2)
        if col1_is_forward:
            data['voltages_forward'] = voltages_1[:mid]
            data['currents_forward'] = currents_1[:mid]
            data['current_densities_forward'] = current_densities_1[:mid]
            data['voltages_reverse'] = voltages_1[mid:]
            data['currents_reverse'] = currents_1[mid:]
            data['current_densities_reverse'] = current_densities_1[mid:]
        else:
            data['voltages_forward'] = voltages_1[mid:]
            data['currents_forward'] = currents_1[mid:]
            data['current_densities_forward'] = current_densities_1[mid:]
            data['voltages_reverse'] = voltages_1[:mid]
            data['currents_reverse'] = currents_1[:mid]
            data['current_densities_reverse'] = current_densities_1[:mid]
    else:
        if col1_is_forward:
            data['voltages_forward'] = voltages_1
            data['currents_forward'] = currents_1
            data['current_densities_forward'] = current_densities_1
            data['voltages_reverse'] = []
            data['currents_reverse'] = []
            data['current_densities_reverse'] = []
        else:
            data['voltages_forward'] = []
            data['currents_forward'] = []
            data['current_densities_forward'] = []
            data['voltages_reverse'] = voltages_1
            data['currents_reverse'] = currents_1
            data['current_densities_reverse'] = current_densities_1

    return data


# todo: when reading profile, the error could be with the spec file
# todo: get filepath from error messages instead of parameter
@contextmanager
def safe_file_operation(file_path: str):
    """
    Context manager which catches common file operation error and prints custom error messages

    :param file_path: path to file being worked on
    """
    global file_op_errors
    file_op_errors = True

    try:
        yield
        # code in 'with' block is effectively executed here
    except FileNotFoundError:
        print('Could not find: ' + file_path, c=gui.ERROR)
    except PermissionError:
        print(f'Permission denied for {os.path.basename(file_path)}', c=gui.ERROR)
        print('Do you have the file open elsewhere?', c=gui.ERROR)
    except OSError as e:
        print(f'Error operating on {os.path.basename(file_path)}', c=gui.ERROR)
        print(e, c=gui.ERROR)
        print('Check inputs and file status, then retry operation', c=gui.IMPORTANT)
        print('If still does not work, report this error and restart app', c=gui.IMPORTANT)
    except Exception as e:
        print(f'Unhandled exception occurred on {os.path.basename(file_path)}', c=gui.ERROR)
        print(e, c=gui.ERROR)
        print('Check inputs and file status, retry operation and/or restart app', c=gui.IMPORTANT)
        print('Please report this error', c=gui.IMPORTANT)
    else:
        file_op_errors = False


def read_profile(file_path: str, spec_file: str):
    if not file_path or not spec_file:
        return None

    with safe_file_operation(file_path):
        if os.path.exists(spec_file):
            config = ConfigObj(file_path, configspec=spec_file, raise_errors=True)
            if not config.validate(Validator()):
                print("Invalid value in profile file", c=gui.ERROR)
                return None
        else:
            print('Missing spec file: profile not validated', c=gui.WARNING)
            config = ConfigObj(file_path, raise_errors=True)
    if not config or file_op_errors:
        return None

    try:
        param = {'area': config["area"],
                 'curr_limit': config["curr_limit"],
                 'start_volt': config["start_volt"],
                 'stop_volt': config["stop_volt"],
                 'volt_step': config["volt_step"],
                 'settle_time': config["settle_time"],
                 'illum': config["illum"],
                 'hysteresis': config["hysteresis"],
                 'curr_density': config["curr_density"]}
    except KeyError as e:
        print(f'Missing value in {os.path.basename(file_path)}: {e}', c=gui.ERROR)
        param = None

    return param


def read_profile2(file_path: str, spec_file: str):
    if not file_path or not spec_file:
        return None

    with safe_file_operation(file_path):
        if os.path.exists(spec_file):
            config = ConfigObj(file_path, configspec=spec_file, raise_errors=True)
            if not config.validate(Validator()):
                print("Invalid value in profile file", c=gui.ERROR)
                return None
        else:
            print('Missing spec file: profile not validated', c=gui.WARNING)
            config = ConfigObj(file_path, raise_errors=True)
    if not config or file_op_errors:
        return None

    try:
        param = {'area': config["area"],
                 'curr_limit': config["curr_limit"],
                 'start_volt': config["start_volt"],
                 'stop_volt': config["stop_volt"],
                 'volt_step': config["volt_step"],
                 'settle_time': config["settle_time"],
                 'illum': config["illum"],
                 'hysteresis': config["hysteresis"],
                 'curr_density': config["curr_density"]}
    except KeyError as e:
        print(f'Missing value in {os.path.basename(file_path)}: {e}', c=gui.ERROR)
        param = None

    return param


def load_profile(file_path: str, spec_file: str, window: PySimpleGUI.Window):
    if not file_path or not spec_file or not window:
        return

    profile = read_profile(file_path, spec_file)

    if not profile:
        return

    window['-AREA-'].update(profile['area'])
    window['-CURR-LIMIT-'].update(profile['curr_limit'])
    window['-START-VOLT-'].update(profile['start_volt'])
    window['-STOP-VOLT-'].update(profile['stop_volt'])
    window['-VOLT-STEP-'].update(profile['volt_step'])
    window['-SETTLE-TIME-'].update(profile['settle_time'])
    window['-ILLUM-'].update(profile['illum'])
    window['-HYSTERESIS-'].update(profile['hysteresis'])
    window['-CURR-DENSITY-'].update(profile['curr_density'])

    print('Loaded profile from ' + os.path.basename(file_path))


def load_profile2(file_path: str, spec_file: str, window: PySimpleGUI.Window):
    if not file_path or not spec_file or not window:
        return

    profile = read_profile2 (file_path, spec_file)

    if not profile:
        return

    window['-area-'].update(profile['area'])
    window['-curr-limit-'].update(profile['curr_limit'])
    window['-start-volt-'].update(profile['start_volt'])
    window['-stop-volt-'].update(profile['stop_volt'])
    window['-volt-step-'].update(profile['volt_step'])
    window['-settle-time-'].update(profile['settle_time'])
    window['-illum-'].update(profile['illum'])
    window['-hysteresis-'].update(profile['hysteresis'])
    window['-curr-densioty-'].update(profile['curr_density'])

    print('Loaded profile from ' + os.path.basename(file_path))


def save_profile(file_path: str, spec_file: str, param: dict):
    if not file_path or not spec_file or not param:
        return

    with safe_file_operation(file_path):  # todo: what is error is specfile?
        if os.path.exists(spec_file):
            config = ConfigObj(file_path, configspec=spec_file, raise_errors=True)
        else:
            print('Missing spec file: profile not validated', c=gui.WARNING)
            config = ConfigObj(file_path, raise_errors=True)
    if not config or file_op_errors:
        return

    config["area"] = param['area']
    config["curr_limit"] = param['curr_limit']
    config["start_volt"] = param['start_volt']
    config["stop_volt"] = param['stop_volt']
    config["volt_step"] = param['volt_step']
    config["settle_time"] = param['settle_time']
    config["illum"] = param['illum']
    config["hysteresis"] = param['hysteresis']
    config["curr_density"] = param['curr_density']

    if os.path.exists(spec_file): # if the path exists, return true
        if not config.validate(Validator()):
            print("Invalid value in profile", c=gui.ERROR)
            return

    with safe_file_operation(file_path):
        config.write()
    if file_op_errors:
        return

    print('Saved profile to ' + os.path.basename(file_path), c=gui.COMPLETE)
   # os.path.basename(path) return the file name

# todo: loading oscilla output files with header and footer
# IV_data = np.genfromtxt("20220407/22-04-07_16-00-37 device 2 Current-Voltage Data.csv", delimiter=',', skip_header=3,
#                         skip_footer=3)
def load_data(file_path: str):
    if not file_path:
        return None

    with safe_file_operation(file_path):
        file_data = read_csv(file_path)
    if file_op_errors:
        return None

    if not file_data.apply(lambda s: to_numeric(s, errors='coerce').notnull().all()).all():
        print('Non numeric data detected', c=gui.ERROR)
        print('Did you try to load an Oscilla file?', c=gui.ERROR)
        return None

    try:
        voltages_1 = file_data['Voltage (V)'].to_list()
        currents_1 = file_data['Current (mA)'].to_list()
        current_densities_1 = file_data['Current Density (mA/cm2)'].to_list()
    except KeyError as e:
        print(f'Could not find column {e} in {os.path.basename(file_path)}', c=gui.ERROR)
        print('Check column naming and try again', c=gui.ERROR)
        return None

    if not voltages_1:
        print('Empty data file', c=gui.ERROR)
        return None

    if not (len(voltages_1) == len(currents_1) == len(current_densities_1)):
        print('Columns are differing lengths', c=gui.ERROR)
        return None

    try:
        # pandas appends '.1' when it detects duplicate column names
        voltages_2 = file_data['Voltage (V).1'].to_list()
        currents_2 = file_data['Current (mA).1'].to_list()
        current_densities_2 = file_data['Current Density (mA/cm2).1'].to_list()
    except KeyError:
        # this file contained only one column set, not a problem
        # todo: or the second set of columns had a naming error
        voltages_2 = currents_2 = current_densities_2 = []

    data = sort_data(voltages_1, voltages_2, currents_1, currents_2, current_densities_1, current_densities_2)

    print('Loaded data from ' + os.path.basename(file_path))
    return data


def save_data(file_path: str, data: dict):
    if not file_path or not data:
        return

    if not data['voltages_forward'] and not data['voltages_reverse']:
        print('No data to save', c=gui.WARNING)
        return

    dir_name = os.path.dirname(file_path)
    with safe_file_operation(dir_name):
        os.makedirs(dir_name, exist_ok=True)
    if file_op_errors:
        return

    headers = ['Voltage (V)', 'Current (mA)', 'Current Density (mA/cm2)']

    # only write data for scans that took place
    if data['voltages_forward'] and data['voltages_reverse']:
        write_data = dict(data)
        headers += headers
    elif not data['voltages_forward']:
        write_data = {'voltages_reverse': data['voltages_reverse'],
                      'currents_reverse': data['currents_reverse'],
                      'current_densities_reverse': data['current_densities_reverse']}
    else:
        write_data = {'voltages_forward': data['voltages_forward'],
                      'currents_forward': data['currents_forward'],
                      'current_densities_forward': data['current_densities_forward']}

    df = DataFrame(data=write_data)

    with safe_file_operation(file_path):
        df.to_csv(file_path, index=False, header=headers)
    if file_op_errors:
        return

    print('Saved data to ' + os.path.basename(file_path), c=gui.COMPLETE)


def save_results(file_path: str, experiment_name: str, results_forward: dict, results_reverse: dict, profile: dict):
    if not file_path or not experiment_name:
        return
    if not profile:
        print('No profile to save', c=gui.WARNING)
        return
    # todo: more concise logic for this?
    if not (results_forward or results_reverse):
        print('No results to save', c=gui.WARNING)
        return
    if not results_reverse and results_forward['J_sc'] == 0:
        print('No results to save', c=gui.WARNING)
        return
    if not results_forward and results_reverse['J_sc'] == 0:
        print('No results to save', c=gui.WARNING)
        return
    if (results_forward and results_reverse) and (results_forward['J_sc'] == results_reverse['J_sc'] == 0):
        print('No results to save', c=gui.WARNING)
        return

    headers = ['Date', 'Time', 'Experiment Name', 'Scan Direction', 'J_sc (mA/cm2)', 'V_oc (V)', 'R_shunt (Ohm)',
               'R_series (Ohm)', 'Max Power (mW/cm2)', 'V_mpp (V)', 'I_mpp (mA)', 'PCE (%)', 'FF (%)', 'Sweep Time (s)',
               'Volt Rate (V/s)', 'Device Area (cm2)', 'Current Limit (mA)', 'Start Volt (V)', 'Stop Volt (V)',
               'Volt Step (V)', 'Settle Time (s)', 'Illumination (mW/cm2)']

    # check if file already has headers
    if os.path.exists(file_path):
        with safe_file_operation(file_path), open(file_path) as file:
            if file.read(1):
                headers = False

    # confirm for/rev scans get proper start/stop volt
    profile_opp = dict(profile)
    profile_opp['start_volt'] = profile['stop_volt']
    profile_opp['stop_volt'] = profile['start_volt']
    profile_forward = profile if profile['stop_volt'] > profile['start_volt'] else profile_opp
    profile_reverse = profile if profile['stop_volt'] < profile['start_volt'] else profile_opp

    date = datetime.now().strftime('%Y/%m/%d')
    time = datetime.now().strftime('%X')

    df = DataFrame()


    if results_forward and results_forward['J_sc'] != 0:
        results_df = DataFrame([date, time, experiment_name, 'forward'] + list(results_forward.values())).transpose()
        profile_df = DataFrame(list(profile_forward.values())[0:-2]).transpose()
        forward_df = concat([results_df, profile_df], axis=1)
        df = concat([df, forward_df])
    if results_reverse and results_reverse['J_sc'] != 0:
        results_df = DataFrame([date, time, experiment_name, 'reverse'] + list(results_reverse.values())).transpose()
        profile_df = DataFrame(list(profile_reverse.values())[0:-2]).transpose()
        reverse_df = concat([results_df, profile_df], axis=1)
        df = concat([df, reverse_df])

    with safe_file_operation(file_path):
        df.to_csv(file_path, index=False, header=headers, mode='a')
    if file_op_errors:
        return

    print('Saved results and profile to ' + os.path.basename(file_path), c=gui.COMPLETE)


