#!/usr/bin/env python3
#
from matplotlib import pyplot as plt
from dateutil import parser
import modules.brondata as brondata
from modules.brondata import decimalstring, intOrZero
from modules.datautil import anotate
from datetime import datetime, date, timedelta

print("------------ %s ------------" % __file__)
if not (brondata.freshdata() or brondata.isnewer(__file__, '../cache/daily-stats.json')):
    print("No fresh data, and unchanged code. Exit.")
    exit(0)
else:
    print("New data, regenerate output.")

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

vaccins_geschat = {
    'x': [],
    'totaal_geschat': []
}

vaccins_geleverd = {
    'x': [],
    'totaal': []
}

date_range = brondata.getDateRange(metenisweten)

def addVaccinCount(record, vaccin):
    count = intOrZero(record[vaccin])
    vaccins_totaal[vaccin].append(count)
    return count


for d in date_range:
    datum = d.strftime("%Y-%m-%d")
    if (datum in metenisweten and metenisweten[datum]['vaccinaties']['astra_zeneca'] != None):
        vaccins_totaal['x'].append(d)

        record = metenisweten[datum]['vaccinaties']
        total = addVaccinCount(record, 'astra_zeneca')\
            + addVaccinCount(record, 'pfizer')\
            + addVaccinCount(record, 'cure_vac')\
            + addVaccinCount(record, 'janssen')\
            + addVaccinCount(record, 'moderna')\
            + addVaccinCount(record, 'sanofi')

        vaccins_totaal['totaal'].append(total)

        # Creer start van schatting grafiek
        vaccins_geschat['x'].append(d)
        vaccins_geschat['totaal_geschat'].append(total)

    if (datum in metenisweten and metenisweten[datum]['vaccinaties']['totaal_geschat'] != None):
        vaccins_geschat['x'].append(d)
        vaccins_geschat['totaal_geschat'].append(metenisweten[datum]['vaccinaties']['totaal_geschat'])

    if (datum in metenisweten and metenisweten[datum]['vaccinaties']['geleverd'] != None):
        vaccins_geleverd['x'].append(d)
        vaccins_geleverd['totaal'].append(metenisweten[datum]['vaccinaties']['geleverd'])


totaal_inwoners=17500000

gezet = vaccins_totaal['totaal'][-1] - vaccins_totaal['totaal'][-2]
nogzetten = ((totaal_inwoners*2) - vaccins_totaal['totaal'][-1])
intijd = (vaccins_totaal['x'][-1] - vaccins_totaal['x'][-2]).days
vaccinsperdag = gezet/intijd
dagentegaan = nogzetten/vaccinsperdag
klaar = (vaccins_totaal['x'][-1] + timedelta(days=dagentegaan)).strftime("%Y-%m-%d")

vaccins_percentage = {
    'x':              vaccins_totaal['x'],
    'astra_zeneca':   [100*x/(totaal_inwoners*2) for x in vaccins_totaal['astra_zeneca']],
    'pfizer':         [100*x/(totaal_inwoners*2) for x in vaccins_totaal['pfizer']],
    'cure_vac':       [100*x/(totaal_inwoners*2) for x in vaccins_totaal['cure_vac']],
    'janssen':        [100*x/(totaal_inwoners*1) for x in vaccins_totaal['janssen']],
    'moderna':        [100*x/(totaal_inwoners*2) for x in vaccins_totaal['moderna']],
    'sanofi':         [100*x/(totaal_inwoners*2) for x in vaccins_totaal['sanofi']],
    'totaal':         [100*x/(totaal_inwoners*2) for x in vaccins_totaal['totaal']],
}

vaccins_geschat_percentage = {
    'x':              vaccins_geschat['x'],
    'totaal_geschat': [100*x/(totaal_inwoners*2) for x in vaccins_geschat['totaal_geschat']]
}

vaccins_geleverd_percentage = {
    'x':              vaccins_geleverd['x'],
    'totaal': [100*x/(totaal_inwoners*2) for x in vaccins_geleverd['totaal']]
}

print('Generating vaccination graph...')
fig, ax1 = plt.subplots(figsize=(10, 5))
fig.subplots_adjust(top=0.92, bottom=0.13, left=0.09, right=0.91)

ax2 = plt.twinx()

ax1.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)

ax2.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)


totaal_prikken_geschat = decimalstring(vaccins_geschat['totaal_geschat'][-1])

percentage_prikken_geschat = decimalstring(round(vaccins_geschat_percentage['totaal_geschat'][-1],2))


ax1.plot(vaccins_geschat_percentage['x'], 
         vaccins_geschat_percentage['totaal_geschat'], 
         linestyle=':', 
         color='fuchsia',
         label='Geprikt geschat (nu: ' + totaal_prikken_geschat + ', ' + percentage_prikken_geschat + '%)')

totaal_vaccins_geleverd = decimalstring(vaccins_geleverd['totaal'][-1])
percentage_vaccins_geleverd = decimalstring(round(100*vaccins_geleverd['totaal'][-1]/(totaal_inwoners*2),2))
ax1.plot(vaccins_geleverd_percentage['x'], 
         vaccins_geleverd_percentage['totaal'], 
         linestyle='--', 
         color='c',
         label='Vaccins geleverd (nu: ' + totaal_vaccins_geleverd + ', ' + percentage_vaccins_geleverd + '%)')

ax2.set_xlabel("Datum")
ax2.set_ylabel("Aantal prikken")

ax2.stackplot(
    vaccins_percentage['x'],
    vaccins_percentage['astra_zeneca'],
    vaccins_percentage['pfizer'],
    vaccins_percentage['cure_vac'],
    vaccins_percentage['janssen'],
    vaccins_percentage['moderna'],
    vaccins_percentage['sanofi'],
    labels=(
        'COVID-19 Vaccine AstraZeneca ® ('+decimalstring(vaccins_totaal['astra_zeneca'][-1])+')',
        'Comirnaty® (BioNTech/Pfizer) ('+decimalstring(vaccins_totaal['pfizer'][-1])+')',
        'CVnCoV (CureVac) ('+decimalstring(vaccins_totaal['cure_vac'][-1])+')',
        'COVID-19 Vaccine Janssen ('+decimalstring(vaccins_totaal['janssen'][-1])+')',
        'COVID-19 Vaccine Moderna ® ('+decimalstring(vaccins_totaal['moderna'][-1])+')',
        'Sanofi/GSK ('+decimalstring(vaccins_totaal['sanofi'][-1])+')'
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

# Let op! Mensen hebben van (de meeste) vaccins twee prikken nodig.
# Dat betekent dat de dashboard data van RIVM ongelofelijk slecht is.
# Omdat we niet weten hoeveel mensen 1x of 2x zijn ingeent, nemen we
# hier even aan dat alle vaccins 2 prikken nodig hebben, EN dat
# die dan  ook bij 1 persoon zijn gezet (dat betekent grofweg dat de data
# van 3 weken terug beter klopt dan de data van vorige week)
totaal_prikken = decimalstring(vaccins_totaal['totaal'][-1])
percentage_prikken = decimalstring(round(vaccins_percentage['totaal'][-1],2))

ax2.plot(vaccins_percentage['x'], 
         vaccins_percentage['totaal'], 
         color='black',
         label='Totaal gerapporteerd (nu: ' + totaal_prikken + ', ' + percentage_prikken + '%)')

graphname='vaccins'
for event in events:
    if graphname in event:
        anotate(
            ax2, 
            vaccins_percentage['x'], vaccins_percentage['totaal'],
            event['date'], event['event'], 
            event[graphname][0], 
            event[graphname][1]
        )

# laat huidige datum zien met vertikale lijn
plt.figtext(0.885,0.125, 
         datetime.now().strftime("%d"), 
         color="red",
         fontsize=8,
         bbox=dict(facecolor='white', alpha=0.9, pad=0,
         edgecolor='white'),
         zorder=10)
ax2.axvline(date.today(), color='red', linewidth=0.5)

ax1.set_yticks      ([10,    20,   30,   40,   50,   60,   70,   80,  90,   100])
ax1.set_yticklabels([ '10%',  '20%', '30%', '40%', '50%', '60%', '70%','80%','90%','100%'])

ax2.set_yticks      ([10,    20,   30,   40,   50,   60,   70,   80,  90,   100])
ax2.set_yticklabels([ '10%',  '20%', '30%', '40%', '50%', '60%', '70%','80%','90%','100%'])

plt.gca().set_xlim([parser.parse("2020-03-01"), date_range[-1]])

ax1.set_ylim([0, 100])
ax2.set_ylim([0, 100])

plt.figtext(0.22,0.42, 
         "Deze grafiek gaat over het totaal aantal gezette prikken \n"+\
         "op basis van beschikbare weekrapportages.\n"+\
         "De huidige vaccins hebben 2 prikken nodig.\n"+\
         "Met het huidig tempo zijn alle prikken gezet op "+klaar+".", 
         color="gray",
         bbox=dict(facecolor='white', alpha=1.0, 
         edgecolor='white'),
         zorder=10)

gegenereerd_op=datetime.now().strftime("%Y-%m-%d %H:%M")
data_tot=vaccins_totaal['x'][-1].strftime("%Y-%m-%d")
filedate=data_tot

plt.title('Gezette prikken (COVID-19 vaccinatie voortgang)')

footerleft="Gegenereerd op "+gegenereerd_op+", o.b.v. data tot "+data_tot+".\nSource code: http://github.com/realrolfje/coronadata"
plt.figtext(0.01, 0.01, footerleft, ha="left", fontsize=8, color="gray")


footerright="Publicatiedatum RIVM "+filedate+".\nBron: https://www.rivm.nl/covid-19-vaccinatie/"
plt.figtext(0.99, 0.01, footerright, ha="right", fontsize=8, color="gray")

ax1.legend(loc="upper right")
ax2.legend(loc="upper left")


plt.savefig("../docs/graphs/vaccinaties.svg", format="svg")
