#!/usr/bin/env python3
#
#

from datetime import datetime, timedelta
import os
from . brondata import freshdata, isnewer, dateCache
from . arguments import isForce
from .defaults import DAILY_STATS

LABEL_ROWS = (0.88, 0.76, 0.64, 0.52, 0.40, 0.28, 0.16)


def place_label(ax, renderer, plot_area, occupied, text, point, label_x, y_maximum):
    """Annotates point with text that does not cover an occupied box. Returns the label box."""
    for row in LABEL_ROWS:
        probe = ax.text(label_x, y_maximum * row, text, fontsize=8, ha='center')
        box = probe.get_window_extent(renderer).padded(6)
        probe.remove()
        inside = (
            box.x0 >= plot_area.x0 and box.x1 <= plot_area.x1
            and box.y0 >= plot_area.y0 and box.y1 <= plot_area.y1
        )
        if (inside and not any(box.overlaps(other) for other in occupied)) or row == LABEL_ROWS[-1]:
            ax.annotate(
                text,
                xy=point,
                xytext=(label_x, y_maximum * row),
                fontsize=8,
                bbox=dict(boxstyle='round,pad=0.4', fc='ivory', alpha=0.7),
                ha='center',
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.1')
            )
            return box


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
    if os.environ.get('CORONADATA_RENDER_ONLY') == '1':
        print("Render-only mode: use existing processed data without downloading or rebuilding it.")
    elif os.environ.get('CORONADATA_DATA_READY') == '1':
        print("Pipeline stages already completed; render the prepared data.")
    elif freshdata():
        print("New data, regenerate output.")
    elif isnewer(filename, DAILY_STATS):
        print("Script newer than the data, regenerate output.")
    elif isForce():
        print("Force, regenerate output.")
    else:
        print("No fresh data, and unchanged code. Exit.")
        exit(0)


