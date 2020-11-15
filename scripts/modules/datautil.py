#!/usr/bin/env python3
#
# Haalt COVID-19 testresultaten op bij RIVM en NICE
#
#

from dateutil import parser

def anotate(plt, xdata, ydata, datum, tekst, x, y):
    try:
        xindex = xdata.index(parser.parse(datum))
    except ValueError:
        return

    if xindex:
        xval = xdata[xindex]
        yval = ydata[xindex]
        plt.annotate(
            tekst,
            xy=(xval, yval),
            xytext=(parser.parse(x), y),
            fontsize=8,
            bbox=dict(boxstyle='round,pad=0.4', fc='ivory', alpha=1),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.1')
        )
