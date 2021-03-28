#!/usr/bin/env python3
#
#

from datetime import datetime, timedelta
from dateutil import parser

def anotate(plt, xdata, ydata, datum, tekst, x, y):
    d = parser.parse(datum)

    if (d < xdata[0]):
        print("Date %s before start of graph, text not displayed: %s" % (datum, tekst))
        return
    elif (xdata[-1] < d):
        print("Date %s after end of graph, text not displayed: %s" % (datum, tekst))
        return

    try:
        xindex = xdata.index(d)
        yval = ydata[xindex]
    except ValueError:
        # Interpolate Y

        t = d
        while True:
            t = t - timedelta(days=1)
            if t in xdata:
                leftX = t
                break

        t = d
        while True:
            t = t + timedelta(days=1)
            if t in xdata:
                rightX = t
                break
        
        leftY = ydata[xdata.index(leftX)]
        rightY = ydata[xdata.index(rightX)]

        distance = (d - leftX) / (rightX - leftX)
        yval = round(leftY + ((rightY - leftY) * distance))

    if (d is not None) and (yval is not None):
        plt.annotate(
            tekst,
            xy=(d, yval),
            xytext=(parser.parse(x), y),
            fontsize=8,
            bbox=dict(boxstyle='round,pad=0.4', fc='ivory', alpha=1),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.1')
        )
    else:
        print("date %s, yval %s, text not displayed: %s" %(str(d), str(yval), tekst))
