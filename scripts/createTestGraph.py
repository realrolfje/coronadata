#!/usr/bin/env python3
#
# pip3 install matplotlib

from matplotlib import pyplot as plt
import matplotlib.patches as patches
from dateutil import parser
from statistics import mean
import datetime
import json
import modules.brondata as brondata

brondata.freshdata()
metenisweten = brondata.readjson('../cache/daily-stats.json')

alpha = {
    'x': [],
    'y': []
}

beta = {
    'x': [],
    'y': []
}

gamma = {
    'x': [],
    'y': [],
    'min': [],
    'max': []
}

delta = {
    'x': [],
    'y': []
}


for datum in metenisweten:

    value = metenisweten[datum]['nu_opgenomen']
    if value:
        alpha['x'].append(parser.parse(datum))
        alpha['y'].append(value)

    value = metenisweten[datum]['nu_opgenomen_lcps']
    if value:
        beta['x'].append(parser.parse(datum))
        beta['y'].append(value)

    value = metenisweten[datum]['nu_op_ic_noncovid_lcps']
    if value:
        gamma['x'].append(parser.parse(datum))
        gamma['y'].append(value)

    value = metenisweten[datum]['nu_op_ic_lcps']
    if value:
        delta['x'].append(parser.parse(datum))
        delta['y'].append(value)
        

print('Generating test graph...')

fig, ax1 = plt.subplots(figsize=(10, 5))

# ax2 = plt.twinx()

#plt.figure(figsize =(10,5))
ax1.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)
# ax2.grid(which='both', axis='both', linestyle='-.',
#          color='gray', linewidth=1, alpha=0.3)

ax1.plot(alpha['x'], alpha['y'], color='red',label='covid opgenomen patiënten NICE (nu '+str(alpha['y'][-1])+')')
ax1.plot(beta['x'], beta['y'], color='orange',label='covid bezette bedden LCPS (nu '+str(beta['y'][-1])+')')
ax1.plot(gamma['x'], gamma['y'], color='blue', label='non-covid bezette IC bedden LCPS (nu '+str(gamma['y'][-1])+')')
ax1.plot(delta['x'], delta['y'], color='cyan', label='covid bezette IC bedden LCPS (nu '+str(delta['y'][-1])+')')

print("NICE: "+str(alpha['y'][-1]))
print("LCPS: "+str(beta['y'][-1]))

# ax1.plot(beta['x'], beta['y'], color='steelblue', label='beta')

# ax2.plot(alpha['x'], alpha['y'], c olor='steelblue', label='alpha')
# ax1.plot(beta['x'], beta['y'], color='green', label='beta/schatting zieken @rolfje obv RNA in RWZI per # inwoners per veiligheidsregio')

# ax1.fill_between(
#     gamma['x'],
#     gamma['min'],
#     gamma['max'],
#     facecolor='steelblue', alpha=0.1, interpolate=True)

ax1.set_xlabel("Datum")
plt.title('Testplot')

ax1.legend(loc="upper left")
#ax2.legend(loc="upper right")
plt.savefig("../docs/graphs/testplot.svg", format="svg")
# plt.savefig("../docs/graphs/testplot.png", format="png", dpi=180/2)
# plt.show()
