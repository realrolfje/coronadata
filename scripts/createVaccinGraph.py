#!/usr/bin/env python3
#
from matplotlib import pyplot as plt
from dateutil import parser
import modules.brondata as brondata
from modules.brondata import decimalstring, smooth
from datetime import datetime, date, timedelta

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
    'totaal': []
}

date_range = brondata.getDateRange(metenisweten)

def addVaccinCount(record, vaccin):
    if (len(vaccins_totaal[vaccin]) > 0):
        vaccins_totaal[vaccin].append(
            vaccins_totaal[vaccin][-1] + record[vaccin]
        )
    else:
        vaccins_totaal[vaccin].append(record[vaccin])
    return record[vaccin]


for d in date_range:
    datum = d.strftime("%Y-%m-%d")
    if (datum in metenisweten and metenisweten[datum]['vaccinaties']['astra_zeneca'] != None):
        vaccins_totaal['x'].append(datum)

        record = metenisweten[datum]['vaccinaties']
        daytotal = addVaccinCount(record, 'astra_zeneca')\
            + addVaccinCount(record, 'pfizer')\
            + addVaccinCount(record, 'cure_vac')\
            + addVaccinCount(record, 'janssen')\
            + addVaccinCount(record, 'moderna')\
            + addVaccinCount(record, 'sanofi')

        if (len(vaccins_totaal['totaal']) > 0):
            vaccins_totaal['totaal'].append(
                vaccins_totaal['totaal'][-1] + daytotal
            )
        else:
            vaccins_totaal['totaal'].append(daytotal)

# Override tot echte data beschikbaar is. Deze data komt uit
# https://www.rivm.nl/covid-19-vaccinatie/wekelijkse-update-deelname-covid-19-vaccinatie-in-nederland
# zie 
vaccins_totaal = {
    'x':            [ parser.parse("2021-01-06"), parser.parse("2021-01-17"), parser.parse("2021-01-24"), parser.parse("2021-01-31"), parser.parse("2021-02-07"), parser.parse("2021-02-14")],        #'x':           
    'astra_zeneca': [                        0,                          0,                          0,                          0,                          0,                          0],          #'astra_zeneca':
    'pfizer':       [                        0,                      77000,                     146612,                     337526,                     552626,                     771227],          #'pfizer': (gecombineerd met AZ, rapportage maakt geen splitsing)      
    'cure_vac':     [                        0,                          0,                          0,                          0,                          0,                          0],          #'cure_vac':    
    'janssen':      [                        0,                          0,                          0,                          0,                          0,                          0],          #'janssen':     
    'moderna':      [                        0,                          0,                          0,                       6000,                      18519,                      22211],          #'moderna':     
    'sanofi':       [                        0,                          0,                          0,                          0,                          0,                          0],          #'sanofi':      
    'totaal':       [                        0,                      77000,                     146612,                     343526,                     571145,                     793438]           #'totaal':      
}

totaal_inwoners=17500000

gezet = vaccins_totaal['totaal'][-1] - vaccins_totaal['totaal'][-2]
nogzetten = ((totaal_inwoners*2) - vaccins_totaal['totaal'][-1])
intijd = (vaccins_totaal['x'][-1] - vaccins_totaal['x'][-2]).days
vaccinsperdag = gezet/intijd
dagentegaan = nogzetten/vaccinsperdag
klaar = (datetime.now() + timedelta(days=dagentegaan)).strftime("%Y-%m-%d")


print('Generating vaccination graph...')
fig, ax1 = plt.subplots(figsize=(10, 5))
fig.subplots_adjust(top=0.92, bottom=0.13, left=0.09, right=0.91)

ax2 = plt.twinx()

ax1.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)

ax2.grid(which='both', axis='both', linestyle='-.',
         color='gray', linewidth=1, alpha=0.3)

ax2.set_xlabel("Datum")
ax2.set_ylabel("Aantal prikken")

ax2.stackplot(
    vaccins_totaal['x'],
    [x/(totaal_inwoners*2) for x in vaccins_totaal['astra_zeneca']],
    [x/(totaal_inwoners*2) for x in vaccins_totaal['pfizer']],
    [x/(totaal_inwoners*2) for x in vaccins_totaal['cure_vac']],
    [x/(totaal_inwoners*2) for x in vaccins_totaal['janssen']],
    [x/(totaal_inwoners*2) for x in vaccins_totaal['moderna']],
    [x/(totaal_inwoners*2) for x in vaccins_totaal['sanofi']],
    labels=(
        'COVID-19 Vaccine AstraZeneca ® ('+decimalstring(vaccins_totaal['astra_zeneca'][-1])+')',
        'Comirnaty® (BioNTech/Pfizer) ('+decimalstring(vaccins_totaal['pfizer'][-1])+')',
        'CVnCoV (CureVac) ('+decimalstring(vaccins_totaal['cure_vac'][-1])+')',
        'janssen ('+decimalstring(vaccins_totaal['janssen'][-1])+')',
        'COVID-19 Vaccine Moderna ® ('+decimalstring(vaccins_totaal['moderna'][-1])+')',
        'Sanofi/GSK ('+decimalstring(vaccins_totaal['sanofi'][-1])+')'
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
percentage_prikken = decimalstring(round((100*vaccins_totaal['totaal'][-1])/(totaal_inwoners*2),2))

ax2.plot(vaccins_totaal['x'], 
         [x/(totaal_inwoners*2) for x in vaccins_totaal['totaal']], 
         color='black',
         label='Totaal (nu: ' + totaal_prikken + ', ' + percentage_prikken + '%)')

def anotate(plt, xdata, ydata, datum, tekst, x, y):
    xval = parser.parse(datum)
    yval = 0.001
    plt.annotate(
        tekst,
        xy=(xval, yval),
        xytext=(parser.parse(x), y/100),
        fontsize=8,
        bbox=dict(boxstyle='round,pad=0.4', fc='ivory', alpha=1),
        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.1')
    )

graphname='vaccins'
for event in events:
    if graphname in event:
        anotate(
            ax2, 
            vaccins_totaal['x'], vaccins_totaal['totaal'],
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

ax1.set_yticks      ([0.1,    0.2,   0.3,   0.4,   0.5,   0.6,   0.7,   0.8,  0.9,   1])
ax1.set_yticklabels([ '10%',  '20%', '30%', '40%', '50%', '60%', '70%','80%','90%','100%'])

ax2.set_yticks      ([0.1,    0.2,   0.3,   0.4,   0.5,   0.6,   0.7,   0.8,  0.9,   1])
ax2.set_yticklabels([ '10%',  '20%', '30%', '40%', '50%', '60%', '70%','80%','90%','100%'])

plt.gca().set_xlim([parser.parse("2020-03-01"), date_range[-1]])

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


ax2.legend(loc="upper left")


plt.savefig("../docs/graphs/vaccinaties.svg", format="svg")
