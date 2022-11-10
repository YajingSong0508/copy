"""
Rayleigh Solar Tech

Source Meter UI project
plotter.py

Plotting data a matplotlib figure

Created on: July 15th, 2022
Created by: Seamus MacInnes

Updated on: August 19th, 2022
Updated by: Seamus MacInnes
"""

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


fig, axes = plt.subplots()
axes.set_xlabel("Voltage (V)")
axes.grid()

figure_canvas_agg = None
toolbar = None


# todo: combine disable and enable functions?
def disable():
    axes.set_facecolor('grey')
    fig.set_facecolor('grey')
    if figure_canvas_agg:
        figure_canvas_agg.draw()


def enable():
    axes.set_facecolor('white')
    fig.set_facecolor('white')
    if figure_canvas_agg:
        figure_canvas_agg.draw()


# stolen (and then adapted) from PySimpleGUI Demo code
# https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Matplotlib_Embedded_Toolbar.py
def create_figure_w_toolbar(canvas, canvas_toolbar):
    global figure_canvas_agg, toolbar
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()

    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()

    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    toolbar = NavigationToolbar2Tk(figure_canvas_agg, canvas_toolbar)
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)


def plot_data(window, data, show_density=False):
    if not window or not data or not (data['voltages_forward'] or data['voltages_reverse']):
        return

    # clear lines without full reset of plot
    lines = axes.get_lines()
    for line in lines:
        line.remove()

    # clear legend
    legend = axes.get_legend()
    if legend:
        legend.remove()

    # add bold axis lines
    axes.axhline(0, color='black')
    axes.axvline(0, c='black')

    y_forward = data['current_densities_forward'] if show_density else data['currents_forward']
    y_reverse = data['current_densities_reverse'] if show_density else data['currents_reverse']
    y_label = "Current Density (mA/cm2)" if show_density else "Current (mA)"

    if data['voltages_forward']:
        axes.plot(data['voltages_forward'], y_forward, 'b-', label='forward scan')
    if data['voltages_reverse']:
        axes.plot(data['voltages_reverse'], y_reverse, 'r-', label='reverse scan')

    x_min = min(data['voltages_forward'] + data['voltages_reverse'])
    x_max = max(data['voltages_forward'] + data['voltages_reverse'])
    if show_density:
        y_min = min(data['current_densities_forward'] + data['current_densities_reverse'])
        y_max = max(data['current_densities_forward'] + data['current_densities_reverse'])
    else:
        y_min = min(data['currents_forward'] + data['currents_reverse'])
        y_max = max(data['currents_forward'] + data['currents_reverse'])

    axes.set_xlim(left=x_min, right=x_max)
    axes.set_ylim(bottom=y_min, top=y_max)
    axes.set_ylabel(y_label)
    axes.legend(loc='lower right')

    plt.tight_layout()

    if not figure_canvas_agg:
        create_figure_w_toolbar(window['-GRAPH-'].TKCanvas, window['-GRAPH-CONTROLS-'].TKCanvas)

    figure_canvas_agg.draw()
    toolbar.update()
