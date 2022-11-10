"""
Rayleigh Solar Tech

Source Meter UI project
communication.py

Functions to communicate with Keithley 2420 SMU

Based of code written by Katherine A. Kim and Boris Dieseldorf of University of Illinois 1/31/2013

Created on: July 18th, 2022
Created by: Seamus MacInnes

Updated on: August 19th, 2022
Updated by: Seamus MacInnes
"""

import time

import numpy as np
import pyvisa
import source_meter_gui as gui

# reroute print statements to the Alerts Multiline element in the gui
print = gui.alert

resource_name = 'GPIB::1'
cancel_measure = False


def connect_to_instrument():
    """
    Connect to the Keithley 2420 SourceMeter

    :return: Keithley as pyvisa object
    """
    print('Attempting connection...', c=gui.IMPORTANT)
    try:
        rm = pyvisa.ResourceManager()
        SrcMeter = rm.open_resource(resource_name)
        if not isinstance(SrcMeter, pyvisa.resources.GPIBInstrument):
            raise pyvisa.errors.VisaIOError
    except pyvisa.errors.VisaIOError:
        print('Failed - Check connection and power', c=gui.ERROR)
        return None
    print('Success', c=gui.IMPORTANT)
    return SrcMeter


def test_communication(SrcMeter):
    """
    Check communication with Keithley

    :param SrcMeter: pyvisa object for Keithley
    """
    if not SrcMeter:
        return False
    print('Attempting communication...', c=gui.IMPORTANT)
    try:
        idn = SrcMeter.query('*IDN?')
        if not idn:
            raise pyvisa.errors.VisaIOError
    except pyvisa.errors.VisaIOError:
        print('Failed - Check device communication settings', c=gui.ERROR)
        return False
    print('Success', c=gui.IMPORTANT)
    return True


def run_IV_test(SrcMeter, profile):
    """
    returns voltage (V) and current (mA)

    :param SrcMeter: pyvisa object for Keithley
    :param profile: test parameters
    :return: voltages, currents, time and volt rate
    """
    if not SrcMeter or not profile:
        return [], [], 0, 0

    start_volt = float(profile['start_volt'])
    stop_volt = float(profile['stop_volt'])
    volt_step = abs(float(profile['volt_step']))
    curr_limit = abs(float(profile['curr_limit'])) / 1000  # mA to A
    settle_time = abs(float(profile['settle_time']))
    hysteresis = profile['hysteresis']

    if start_volt > stop_volt:
        volt_step = -volt_step

    volt_range = max(abs(start_volt), abs(stop_volt))
    voltage_points = np.arange(start_volt, stop_volt+volt_step/2, volt_step)

    if hysteresis:
        voltage_points = np.concatenate((voltage_points, np.flip(voltage_points)))

    print("Running test...", c=gui.IMPORTANT)

    voltages = []
    currents = []
    elapsed = 0
    volt_rate = 0

    try:
        # configure meter for voltage testing
        SrcMeter.write('*RST')  # Reset GPIB Defaults
        SrcMeter.write(':SYST:BEEP:STAT OFF')  # Turn off beeper
        SrcMeter.write(':SYST:RSEN OFF')  # Turn off 4-wire sensing
        SrcMeter.write(':SOUR:FUNC VOLT')  # Set voltage mode
        SrcMeter.write(':SOUR:VOLT:MODE FIX')  # Fixed source mode
        SrcMeter.write(':SENS:FUNC "CURR"')  # Set-up current measurement
        SrcMeter.write(':SOUR:VOLT:RANG ' + str(volt_range))  # Set acceptable voltage range
        SrcMeter.write(':SENS:CURR:PROT ' + str(curr_limit))  # Set compliance current range
        SrcMeter.write(':SOUR:VOLT:LEV 0')  # start at 0V
        SrcMeter.write(':OUTP ON')  # turn on output

        start = time.time()

        # set and then measure I and V for each point
        for voltage in voltage_points:
            if cancel_measure:
                print('Canceled', c=gui.WARNING)
                break

            SrcMeter.write(':SOUR:VOLT:LEV ' + str(voltage))
            time.sleep(settle_time)

            result = SrcMeter.query(':READ?').split(',')  # todo: add timeout? no parameter for that
            try:
                voltages.append(float(result[0]))  # Volts
                currents.append(float(result[1]) * 1000)  # Amps to milli-amps

                # check against current limit (in amps) with tolerance of 0.1mA
                if abs(float(result[1])) >= curr_limit - 1e-4:
                    print('Current limit reached', c=gui.ERROR)
                    break

            except (ValueError, IndexError):
                print('Unexpected Response', c=gui.ERROR)
                break

        else:
            print('Completed', c=gui.COMPLETE)

        elapsed = time.time() - start  # printing the outcome takes ~1ms

        SrcMeter.write(":OUTP OFF")  # Turn off the source output

        volt_range = abs(stop_volt - start_volt) * 2 if hysteresis else abs(stop_volt - start_volt)
        volt_rate = volt_range / elapsed

    except pyvisa.errors.VisaIOError as e:
        print('Communication Failure', c=gui.ERROR)
        print(e, c=gui.ERROR)


    return voltages, currents, elapsed, volt_rate

def run_lifespan_test(SrcMeter, profile):
    """
    returns voltage (V) and current (mA)

    :param SrcMeter: pyvisa object for Keithley
    :param profile: test parameters
    :return: voltages, currents, time and volt rate
    """
    if not SrcMeter or not profile:
        return [], [], 0, 0

    start_volt = float(profile['start_volt'])
    stop_volt = float(profile['stop_volt'])
    volt_step = abs(float(profile['volt_step']))
    curr_limit = abs(float(profile['curr_limit'])) / 1000  # mA to A
    settle_time = abs(float(profile['settle_time']))
    hysteresis = profile['hysteresis']

    if start_volt > stop_volt:
        volt_step = -volt_step

    volt_range = max(abs(start_volt), abs(stop_volt))
    voltage_points = np.arange(start_volt, stop_volt+volt_step/2, volt_step)

    if hysteresis:
        voltage_points = np.concatenate((voltage_points, np.flip(voltage_points)))

    print("Running test...", c=gui.IMPORTANT)

    voltages2 = []
    currents2 = []
    elapsed2 = 0
    volt_rate2 = 0

    try:
        # configure meter for voltage testing
        SrcMeter.write('*RST')  # Reset GPIB Defaults
        SrcMeter.write(':SYST:BEEP:STAT OFF')  # Turn off beeper
        SrcMeter.write(':SYST:RSEN OFF')  # Turn off 4-wire sensing
        SrcMeter.write(':SOUR:FUNC VOLT')  # Set voltage mode
        SrcMeter.write(':SOUR:VOLT:MODE FIX')  # Fixed source mode
        SrcMeter.write(':SENS:FUNC "CURR"')  # Set-up current measurement
        SrcMeter.write(':SOUR:VOLT:RANG ' + str(volt_range))  # Set acceptable voltage range
        SrcMeter.write(':SENS:CURR:PROT ' + str(curr_limit))  # Set compliance current range
        SrcMeter.write(':SOUR:VOLT:LEV 0')  # start at 0V
        SrcMeter.write(':OUTP ON')  # turn on output

        start = time.time()

        # set and then measure I and V for each point
        for voltage in voltage_points:
            if cancel_measure:
                print('Canceled', c=gui.WARNING)
                break

            SrcMeter.write(':SOUR:VOLT:LEV ' + str(voltage))
            time.sleep(settle_time)

            result = SrcMeter.query(':READ?').split(',')  # todo: add timeout? no parameter for that
            try:
                voltages.append(float(result[0]))  # Volts
                currents.append(float(result[1]) * 1000)  # Amps to milli-amps

                # check against current limit (in amps) with tolerance of 0.1mA
                if abs(float(result[1])) >= curr_limit - 1e-4:
                    print('Current limit reached', c=gui.ERROR)
                    break

            except (ValueError, IndexError):
                print('Unexpected Response', c=gui.ERROR)
                break

        else:
            print('Completed', c=gui.COMPLETE)

        elapsed = time.time() - start  # printing the outcome takes ~1ms

        SrcMeter.write(":OUTP OFF")  # Turn off the source output

        volt_range = abs(stop_volt - start_volt) * 2 if hysteresis else abs(stop_volt - start_volt)
        volt_rate = volt_range / elapsed

    except pyvisa.errors.VisaIOError as e:
        print('Communication Failure', c=gui.ERROR)
        print(e, c=gui.ERROR)


    return voltages, currents, elapsed, volt_rate

# Sweep operation - all data comes in one read
# SrcMeter.write('*RST')
# SrcMeter.write(':SENS:FUNC:CONC OFF')
# SrcMeter.write(':SOUR:FUNC VOLT')
# SrcMeter.write(':SENS:FUNC \'CURR:DC\'')
# SrcMeter.write(':SENS:CURR:PROT 0.1')
# SrcMeter.write(':SOUR:VOLT:START 1E-3')
# SrcMeter.write(':SOUR:VOLT:STOP 10E-3')
# SrcMeter.write(':SOUR:VOLT:STEP 1E-3')
# SrcMeter.write(':SOUR:VOLT:MODE SWE')
# SrcMeter.write(':SOUR:SWE:RANG AUTO')
# SrcMeter.write(':SOUR:SWE:SPAC LIN')
# SrcMeter.write(':TRIG:COUN 10')
# SrcMeter.write(':SOUR:DEL 0.1')
# SrcMeter.write(':OUTP ON')
# output = SrcMeter.query(':READ?')
# print(output)
# SrcMeter.write(':OUTP OFF')
