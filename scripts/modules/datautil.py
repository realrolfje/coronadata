#!/usr/bin/env python3
#
#

from datetime import datetime, timedelta
from sre_compile import isstring
from . brondata import freshdata, isnewer, dateCache
from . arguments import isForce

def anotate(plt, xdata, ydata, datum, tekst, x, y):
    if isinstance(datum, str):
        d = dateCache.parse(datum)
    else:
        d = datum

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
        if isinstance(x, str):
            xx = dateCache.parse(x)
        else :
            xx = x

        plt.annotate(
            tekst,
            xy=(d, yval),
            xytext=(xx, y),
            fontsize=8,
            bbox=dict(boxstyle='round,pad=0.4', fc='ivory', alpha=0.5),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.1', alpha=0.5)
        )
    else:
        print("date %s, yval %s, text not displayed: %s" %(str(d), str(yval), tekst))


def runIfNewData(filename):
    print("------------ %s ------------" % filename)
    if freshdata():
        print("New data, regenerate output.")
    elif isnewer(filename, '../data/daily-stats.json'):
        print("Script newer than the data, regenerate output.")
    elif isForce():
        print("Force, regenerate output.")
    else:
        print("No fresh data, and unchanged code. Exit.")
        exit(0)


