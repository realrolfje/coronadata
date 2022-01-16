#!/usr/bin/env python3
#
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

#brondata.freshdata()
metenisweten = brondata.readjson('../cache/daily-stats.json')
events = brondata.readjson('../data/measures-events.json')

vaccins_totaal = {
    'x': [],
    'astra_zeneca': [],
    'pfizer': [],
    'cure_vac': [],
    'janssen': [],
    'moderna': [],
    'sanofi': [],
    'totaal': [],
}

vaccins_delta = {
    'x': [],
    'astra_zeneca': [],
    'pfizer': [],
    'cure_vac': [],
    'janssen': [],
    'moderna': [],
    'sanofi': [],
    'totaal': [],
}


date_range = brondata.getDateRange(metenisweten)
plot_range = date_range

lastDays = arguments.lastDays()
if (lastDays>0):
    plot_range = date_range[-(lastDays+14):]
    date_range = date_range[-lastDays:]

def addVaccinCount(record, vaccin):
    count = intOrZero(record[vaccin])
    vaccins_totaal[vaccin].append(count)
    return count

allvacins = ['astra_zeneca', 'pfizer', 'cure_vac', 'janssen','moderna', 'sanofi']

for d in plot_range:
    datum = d.strftime("%Y-%m-%d")
    if (datum in metenisweten and metenisweten[datum]['vaccinaties']['astra_zeneca'] != None):
        vaccins_totaal['x'].append(d)

        record = metenisweten[datum]['vaccinaties']

        total = 0
        for vaccin in allvacins:
            total +=  addVaccinCount(record, vaccin)
        vaccins_totaal['totaal'].append(total)

        if len(vaccins_totaal['x']) > 1:
            vaccins_delta['x'].append(d)

            days = (d - vaccins_totaal['x'][-2]).days

            vaccins_delta['totaal'].append(
                round(
                    max(0,
                        (intOrZero(record['totaal']) - vaccins_totaal['totaal'][-2]) / days
                    )
                )
            )
            for vaccin in allvacins:
                vaccins_delta[vaccin].append(
                    round(
                        max(0,
                            (intOrZero(record[vaccin]) - vaccins_totaal[vaccin][-2]) / days
                        )
                    )
                )


print('Generating vaccination graph...')
fig, ax1 = plt.subplots(figsize=(10, 5))
fig.subplots_adjust(top=0.92, bottom=0.13, left=0.09, right=0.91)

# ax2 = plt.twinx()

ax1.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)

# ax1.grid(which='both', axis='both', linestyle='-.',
#          color='gray', linewidth=1, alpha=0.3)

ax1.set_xlabel("Datum")
ax1.set_ylabel("Prikken per dag")

ax1.stackplot(
    vaccins_delta['x'],
    vaccins_delta['astra_zeneca'],
    vaccins_delta['pfizer'],
    vaccins_delta['cure_vac'],
    vaccins_delta['janssen'],
    vaccins_delta['moderna'],
    vaccins_delta['sanofi'],
    labels=(
        'COVID-19 Vaccine AstraZeneca ® (%s)' % decimalstring(vaccins_delta['astra_zeneca'][-1]),
        'Comirnaty® (BioNTech/Pfizer) (%s)'   % decimalstring(vaccins_delta['pfizer'][-1]),
        'CVnCoV (CureVac) (%s)'               % decimalstring(vaccins_delta['cure_vac'][-1]),
        'COVID-19 Vaccine Janssen (%s)'       % decimalstring(vaccins_delta['janssen'][-1]),
        'COVID-19 Vaccine Moderna ® (%s)'     % decimalstring(vaccins_delta['moderna'][-1]),
        'Sanofi/GSK (%s)'                     % decimalstring(vaccins_delta['sanofi'][-1])
    ),
    colors=(
        'mediumblue',
        'deepskyblue',
        'darkorange',
        'tomato',
        'yellow',
        'limegreen',
    ),
    baseline='zero'
)

totaal_prikken = decimalstring(vaccins_delta['totaal'][-1])

ax1.plot(vaccins_delta['x'], 
         vaccins_delta['totaal'], 
         color='black',
         label='Totaal per dag (nu: %s)' % totaal_prikken)

graphname='vaccins'
for event in events:
    if graphname in event \
        and dateCache.parse(event[graphname][0]) > date_range[0]\
        and (len(event[graphname]) <= 2 or len(date_range) <= event[graphname][2]):
        anotate(
            ax1, 
            vaccins_delta['x'], vaccins_delta['totaal'],
            event['date'], event['event'], 
            event[graphname][0], 
            event[graphname][1]
        )

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

ax1.set_ylim([0, 400000])
ax1.set_yticks      ([50000, 100000, 150000, 200000, 250000, 300000, 350000, 400000 ])
ax1.set_yticklabels([ '50k', '100k', '150k', '200k', '250k', '300k',  '350k', '400k'])

plt.gca().set_xlim([date_range[0], date_range[-1]])

ax1.set_ylim([0, 400000])
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
data_tot=vaccins_totaal['x'][-1].strftime("%Y-%m-%d")
filedate=data_tot

plt.title('Gezette prikken per dag (COVID-19 vaccinatiesnelheid)')

footerleft="Gegenereerd op "+gegenereerd_op+", o.b.v. data tot "+data_tot+".\nSource code: http://github.com/realrolfje/coronadata"
plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")


footerright="Publicatiedatum RIVM "+filedate+".\nBron: https://www.rivm.nl/covid-19-vaccinatie/"
plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

ax1.legend(loc="upper left")
# ax2.legend(loc="upper left")


if (lastDays > 0):
    plt.savefig("../docs/graphs/vaccinaties-"+str(lastDays)+".svg", format="svg")
else:
    plt.savefig("../docs/graphs/vaccinaties.svg", format="svg")

dateCache.cacheReport()