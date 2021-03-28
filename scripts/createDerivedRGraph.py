#!/usr/bin/env python3
#
# pip3 install matplotlib

from matplotlib import pyplot as plt
from dateutil import parser
import modules.brondata as brondata

print("------------ %s ------------" % __file__)
if not (brondata.freshdata() or brondata.isnewer(__file__, '../cache/daily-stats.json')):
    print("No fresh data, and unchanged code. Exit.")
    exit(0)
else:
    print("New data, regenerate output.")

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
    'y': []
}

delta = {
    'x': [],
    'y': []
}

epsilon = {
    'x': [],
    'y': []
}

# Load
for datum in metenisweten:
    value = metenisweten[datum]['RNA']['besmettelijk']
    if value:
        alpha['x'].append(parser.parse(datum))
        alpha['y'].append(value)

    value = metenisweten[datum]['Rt_avg']
    if value:
        beta['x'].append(parser.parse(datum))
        beta['y'].append(value)

    value = metenisweten[datum]['positief']
    if value:
        delta['x'].append(parser.parse(datum))
        delta['y'].append(value)


# Calculate
#delta['y'] = brondata.smooth(delta['y'])
delta['y'] = brondata.double_savgol(delta['y'], 1, 13, 1)

for i, datum in enumerate(alpha['x']):
    # R = RNA(x+1)/RNA(x)
    if i > 1:
        value = alpha['y'][i] / alpha['y'][i-1]
        if value:
            gamma['x'].append(datum)
            gamma['y'].append(value)

for i, datum in enumerate(delta['x']):
    # R = RNA(x+1)/RNA(x)
    if i > 1:
        value = delta['y'][i] / delta['y'][i-1]
        if value:
            epsilon['x'].append(datum)
            epsilon['y'].append(value)


print('Generating test graph...')

fig, ax1 = plt.subplots(figsize=(10, 5))
ax2 = plt.twinx()

#plt.figure(figsize =(10,5))
# ax1.grid(which='both', axis='both', linestyle='-.',
#          color='gray', linewidth=1, alpha=0.3)
ax2.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)

ax1.plot(alpha['x'], [y /100 for y in alpha['y']], color='blue',label='Besmet obv riooldata')
ax1.plot(delta['x'], delta['y'], color='red', label='positief getest')

ax2.plot(beta['x'], beta['y'], color='lightgray',label='R(t) van RIVM')

ax2.plot(gamma['x'], gamma['y'], color='cyan', label='RNA(x)/RNA(x-1)')
ax2.plot(epsilon['x'], epsilon['y'], color='orange', label='positief(x)/positief(x-1)')


# ax1.plot(beta['x'], beta['y'], color='steelblue', label='beta')

# ax2.plot(alpha['x'], alpha['y'], c olor='steelblue', label='alpha')
# ax1.plot(beta['x'], beta['y'], color='green', label='beta/schatting zieken @rolfje obv RNA in RWZI per # inwoners per veiligheidsregio')

# ax1.fill_between(
#     gamma['x'],
#     gamma['min'],
#     gamma['max'],
#     facecolor='steelblue', alpha=0.1, interpolate=True)

ax1.set_xlabel("Datum")
plt.title('Test RNA berekening')

ax1.legend(loc="upper left")
ax2.legend(loc="upper right")
plt.savefig("../docs/graphs/derivedRgraph.svg", format="svg")
# plt.savefig("../docs/graphs/testplot.png", format="png", dpi=180/2)
# plt.show()
