# -*- coding: utf-8 -*-
"""
Rayleigh Solar Tech

Source Meter UI project
calculations.py

Functions to calculate parameters of solar cells

Created on: July 10th, 2022
Created by: Ajan Ramachandran

Updated on: August 19th, 2022
Updated by: Seamus MacInnes
"""

import numpy as np
import source_meter_gui as gui

# reroute print statements to the Alerts Multiline element in the gui
print = gui.alert


def find_nearest(array: list, value: float):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def calculate_params(voltage: list, current: list, area: float, illum: float):
    """
    Calculate common solar cell parameters. Data is from one scan (either forward or reverse)

    :param voltage: volts
    :param current: milli-amps
    :param area: cm2
    :param illum: mW/cm2
    :return: dict of cell parameters
    """
    if not voltage or not current or not area or not illum:
        return None

    params = {'J_sc': 0, 'V_oc': 0, 'R_sh': 0, 'R_s': 0, 'max_power': 0, 'V_mpp': 0, 'I_mpp': 0, 'PCE': 0, 'FF': 0}

    # confirm order is low to high voltage
    if not np.all(np.diff(voltage) > 0):
        voltage = np.flipud(voltage)
        current = np.flipud(current)

    V_oc = np.interp(0.0, current, voltage)  # if it doesn't cross, returns voltage[0] or voltage[-1]
    J_sc = np.interp(0.0, voltage, current)

    V_intercept = find_nearest(voltage, V_oc)  # index of the closest actual measurement
    J_intercept = find_nearest(current, J_sc)

    # if didn't cross and didn't come close enough
    # todo: how close is close enough? default is 1e-8
    if np.isclose(current[J_intercept], J_sc) and not np.isclose(voltage[J_intercept], 0.0):
        print('Data does not cross or touch 0V', c=gui.WARNING)
    elif np.isclose(voltage[V_intercept], V_oc) and not np.isclose(current[V_intercept], 0.0):
        print('Data does not cross or touch 0mA', c=gui.WARNING)
    else:

        if J_sc >= -0.1:  # todo: better jsc limit - dependant on illumination? remove? could make divide by zero error
            print('Cell J_sc too low - results may be inaccurate', c=gui.WARNING)
        if np.isclose(J_sc, 0.0):  # confirm J_sc is not zero
            J_sc = 0.0000001

        # todo: gradient at each point is average of slope with prev point and slope with next point?
        J_grad = np.diff(current)
        V_grad = np.absolute(voltage[0] - voltage[1])  # volt step same everywhere

        # already know that the intercept is close enough, avoid index out of bounds
        if J_intercept == len(J_grad):
            J_intercept -= 1
            print('Not enough values past 0V', c=gui.WARNING)
        if V_intercept == len(J_grad):
            V_intercept -= 1
            print('Not enough values past 0mA', c=gui.WARNING)

        R_sh = (V_grad / np.abs(J_grad[J_intercept])) * 1E3
        R_s = (V_grad / np.abs(J_grad[V_intercept])) * 1E3

        power = np.multiply(voltage, current)

        max_power = np.amin(power)  # b/c power elements are all negative
        mpp_index = np.where(power == max_power)[0][0]  # tuple with ndarray with int

        V_mpp = voltage[mpp_index]
        I_mpp = current[mpp_index]

        PCE = abs(-(max_power / illum) )* 100
        FF = V_mpp * I_mpp / (V_oc * J_sc) * 100

        # scaling values
        max_power /= area
        PCE /= area
        J_sc /= area
        I_mpp /= area

        params = {'J_sc': J_sc, 'V_oc': V_oc, 'R_sh': R_sh, 'R_s': R_s, 'max_power': max_power, 'V_mpp': V_mpp,
                  'I_mpp': I_mpp, 'PCE': PCE, 'FF': FF}

    return params
