#!/usr/bin/env python3
#
from http.client import CannotSendRequest
from matplotlib import pyplot as plt
from dateutil import parser
import modules.brondata as brondata
import modules.arguments as arguments
from modules.brondata import decimalstring, intOrZero, dateCache
from modules.datautil import anotate
from datetime import datetime, date, timedelta
import sys
from modules.datautil import runIfNewData

runIfNewData(__file__)

varianten = brondata.readjson('../cache/COVID-19_varianten.json')
metenisweten = brondata.readjson('../cache/daily-stats.json')
# events = brondata.readjson('../data/measures-events.json')


varianten_map = {
    # datum : {
    #     code : {
    #       cases: 0,
    #       size: 0
    #     }
    # }
}

varianten_totaal = {
    'x': [],
    # 'variant code' : percentage
    'totaal': [],
}

# Build unique complete set of variant codes and add add array placeholders
variantcodes = {}
for record in varianten:
    if record['Variant_code'] not in variantcodes:
        varianten_totaal[record['Variant_code']] = []
        if record['Variant_name'] == '':
            variantcodes[record['Variant_code']] = record['Variant_code']
        else:
            variantcodes[record['Variant_code']] = "%s (%s)" % (record['Variant_name'], record['Variant_code'])

for record in varianten:
    if record['May_include_samples_listed_before']:
        continue

    d = record['Date_of_statistics_week_start']
    c = record['Variant_code']

    if d not in varianten_map:
      varianten_map[d] = {}

    if c not in varianten_map[d]:
        varianten_map[d][c] = {}

    varianten_map[d][c]['cases'] = record['Variant_cases']
    varianten_map[d][c]['size'] = record['Sample_size']

for key in varianten_map:
    varianten_totaal['x'].append( dateCache.parse(key) )
    for variantcode in variantcodes.keys():
        if variantcode in varianten_map[key]:
            percentage = varianten_map[key][variantcode]['cases']/varianten_map[key][variantcode]['size']
        else:
            percentage = 0
        geschat_ziek = metenisweten[key]['rolf_besmettelijk']    
        varianten_totaal[variantcode].append(percentage * geschat_ziek)

dominance = []
for i in range(len(varianten_totaal['x'])):
    n = 0
    dominant = ''
    for code in variantcodes:
        if varianten_totaal[code][i] > n:
            n = varianten_totaal[code][i]
            dominant = code
    dominance.append(dominant)

# top 10:
totals = {}
for code in variantcodes:
    totals[code] = sum(varianten_totaal[code])
totals=dict(sorted(totals.items(),key=lambda x:x[1]))
top_variants=[]
for k in totals.keys(): top_variants.append(k)
top_variants=top_variants[-5:]

print("Top variants are: %s" % top_variants)

varianten_totaal['overig'] = [0] * len(varianten_totaal['x'])
varianten_totaal['totaal'] = [0] * len(varianten_totaal['x'])
for key in variantcodes:
    varianten_totaal['totaal'] = [ x + y for x,y in zip(varianten_totaal['totaal'], varianten_totaal[key])]
    if key not in top_variants and key != 'x' and key != 'totaal':
        varianten_totaal['overig'] = [ x + y for x,y in zip(varianten_totaal['overig'], varianten_totaal[key])]
        varianten_totaal.pop(key, None)

# record['Variant_code'],
# record['Variant_name'],
# record['ECDC_category'],
# record['WHO_category'],
# record['May_include_samples_listed_before'],
# record['Sample_size'],
# record['Variant_cases']

date_range = brondata.getDateRange(metenisweten)
lastDays = arguments.lastDays()
if (lastDays>0):
    date_range = date_range[-lastDays:]

print('Generating variants graph...')
fig, ax1 = plt.subplots(figsize=(10, 5))
fig.subplots_adjust(top=0.92, bottom=0.13, left=0.09, right=0.91)

ax1.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)

ax1.set_xlabel("Datum")
ax1.set_ylabel("Geschat aantal personen ziek")

# Variants in order of today's 
today = {}
for code in varianten_totaal:
    if code != 'x':
        today[code] = varianten_totaal[code][-1]
today=dict(sorted(today.items(),key=lambda x:x[1]))

yrray = []
ylabels = []

# yrray.append(varianten_totaal['totaal'])
# ylabels.append('Totaal')

yrray.append(varianten_totaal['overig'])
ylabels.append("Overig (nu: %s)" % (decimalstring(round(varianten_totaal['overig'][-1]))))

for code in today:
    if code in varianten_totaal and code in variantcodes:
        yrray.append(varianten_totaal[code])
        ylabels.append("%s (nu: %s)" % (variantcodes[code],decimalstring(round(varianten_totaal[code][-1]))))

ax1.stackplot(
    varianten_totaal['x'],
    *yrray,
    labels=ylabels,
    colors=( # note these are in reverse order because we revert the labels later
        'gray',
        'limegreen',
        'yellow',
        # 'darkorange',
        'mediumslateblue',
        'tomato',
        'deepskyblue',
    ),
    baseline='zero'
)


# print('reversed %s' % ax1.legend().legendHandles)
# totaal_prikken = decimalstring(vaccins_delta['totaal'][-1])

# ax1.plot(vaccins_delta['x'], 
#          vaccins_delta['totaal'], 
#          color='black',
#          label='Totaal per dag (nu: %s)' % totaal_prikken)


for i in range(len(dominance)):
    if i > 2  and dominance[i] != dominance[i-1]:
        ax1.annotate(
            "Dominant:\n%s" % (variantcodes[dominance[i]]),
            xy=(varianten_totaal['x'][i], varianten_totaal['totaal'][i]),
            xytext=(varianten_totaal['x'][i], varianten_totaal['totaal'][i] + 40000),
            fontsize=8,
            bbox=dict(boxstyle='round,pad=0.4', fc='ivory', alpha=1),
            ha='center',
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.1')
        )
  

# graphname='variants'
# for event in events:
#     if graphname in event \
#         and dateCache.parse(event[graphname][0]) > date_range[0]\
#         and (len(event[graphname]) <= 2 or len(date_range) <= event[graphname][2]):
#         anotate(
#             ax1, 
#             vaccins_delta['x'], vaccins_delta['totaal'],
#             event['date'], event['event'], 
#             event[graphname][0], 
#             event[graphname][1]
#         )

# Put vertical line at current day
plt.text(
    x=dateCache.today(),
    y=0,
    s=datetime.now().strftime("%d"), 
    color="white",
    fontsize=8,
    ha="center",
    va="center",
    bbox=dict(boxstyle='round,pad=0.1', facecolor='red', alpha=1, edgecolor='red'),
    zorder=10
)
plt.axvline(dateCache.today(), color='red', linewidth=0.5)
plt.gca().set_xlim([date_range[0], date_range[-1]])

# ax1.set_ylim([0, 400000])
# ax2.set_ylim([0, 100])

# plt.figtext(0.10,0.50, 
#          "Deze grafiek toont hoeveel % van de Nederlanders\n"+\
#          "met de gezette prikken 100% gevaccineerd zouden\n"+\
#          "kunnen zijn. Met het huidig tempo zijn alle prikken\n"+\
#          "gezet op "+klaar+".", 
#          fontsize=8,
#          color="gray",
#          bbox=dict(facecolor='white', alpha=1.0, 
#          edgecolor='white'),
#          zorder=10)

gegenereerd_op=datetime.now().strftime("%Y-%m-%d %H:%M")
data_tot=varianten_totaal['x'][-1].strftime("%Y-%m-%d")
filedate=data_tot

plt.title('Besmettelijke personen per COVID-19 variant')

footerleft="Gegenereerd op "+gegenereerd_op+", o.b.v. data tot "+data_tot+".\nSource code: http://github.com/realrolfje/coronadata"
plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")


footerright="Publicatiedatum RIVM "+filedate+".\nBron: https://data.rivm.nl/covid-19/COVID-19_varianten.json + besmettingdata"
plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

# Reverse sort the legend and place upper left
handles, labels = ax1.get_legend_handles_labels()   #get the handles
ax1.legend(reversed(handles), reversed(labels), loc="upper left")

# ax2.legend(loc="upper left")


if (lastDays > 0):
    plt.savefig("../docs/graphs/variants-"+str(lastDays)+".svg", format="svg")
else:
    plt.savefig("../docs/graphs/variants.svg", format="svg")

dateCache.cacheReport()