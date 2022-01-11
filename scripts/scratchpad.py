#!/usr/bin/env python3
#
from matplotlib import pyplot as plt

x = [0,1,2,3,4,5, 0,1,2,3,4,5]
y = [1,1,2,5,2,3, 1,2,2,5,2,1]


fig, heatmap = plt.subplots(figsize=(10, 4), constrained_layout=True, sharex='all', sharey='all')
fig.subplots_adjust(top=0.92, bottom=0.17, left=0.09, right=0.91)

heatmap.hist2d(
    x, y, 
    bins=[5,5], range=[[0,5],[0,5]], 
    cmin=1, cmap='Blues'
)

averages = plt.twinx()
averages.plot(
    [0,1,2,3,4,5], 
    [5,4,3,2,1,0], 
    color='darkred', alpha=0.5, 
    label='average'
)

averages.axvline(4, color='red', linewidth=0.5)

averages.legend(loc="upper right")

plt.figtext(0.01, 0.01, "test left footer text", ha="left", fontsize=8, color="gray")
plt.figtext(0.99, 0.01, "test right footer text", ha="right", fontsize=8, color="gray")

heatmap.grid(which='both', axis='both', linestyle='-.',
            color='gray', linewidth=1, alpha=0.3)


plt.show()