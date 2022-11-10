
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
import numpy as np

fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
fig.subplots_adjust(hspace=2)
ax1.set_xlim(0.0, 0.20)
ax1.set_ylim(0, 100)
ax1.yaxis.set_ticks(np.arange(0, 101, 50))
ax1.set_ylabel('PCE(%)')

ax2.set_xlim(0.0, 0.20)
ax2.set_ylim(0, 101)
ax2.plot('b-')
ax2.set_ylabel('FF(%)')

ax3.set_xlim(0.0, 0.20)
ax3.set_ylim(0, 100)
ax3.plot('b-')
ax3.set_ylabel('Joc(%)')


ax4.set_xlim(0.0, 0.20)
ax4.set_ylim(0, 100)
ax4.plot('b-')
ax4.set_ylabel('Voc(%)')



figure_canvas_agg2 = None
toolbar2 = None


# stolen (and then adapted) from PySimpleGUI Demo code
# https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Matplotlib_Embedded_Toolbar.py
def create_figure_w_toolbar2(canvas, canvas_toolbar):
    global figure_canvas_agg2, toolbar2
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()

    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()

    figure_canvas_agg2 = FigureCanvasTkAgg(fig, master=canvas)
    toolbar2 = NavigationToolbar2Tk(figure_canvas_agg2, canvas_toolbar)
    figure_canvas_agg2.get_tk_widget().pack(side='right', fill='both', expand=1)

def clear_plot():

    lines = ax1.get_lines()
    for line in lines:
        line.remove()

    # clear legend
    legend = ax1.get_legend()
    if legend:
        legend.remove()


def plot_subplots(window, x,y):
   # if not window or not x or not y:
       # return



    ax1.plot(x,y,"-")

    plt.tight_layout()

    if not figure_canvas_agg2:
        create_figure_w_toolbar2(window['-graph-'].TKCanvas, window['-graph-controls-'].TKCanvas)

    figure_canvas_agg2.draw()
    toolbar2.update()