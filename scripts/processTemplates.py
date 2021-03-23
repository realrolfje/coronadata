#!/usr/bin/env python3
#
import modules.brondata as brondata
from modules.brondata import decimalstring
import datetime
from string import Template
from dateutil import parser
from os import listdir
from os.path import isfile, join, basename
import csv

templatedir = '../docs/templates'
outputdir = '../docs'

brondata.freshdata()
metenisweten = brondata.readjson('../cache/daily-stats.json')

gemiddeldeleeftijdarray=[]
# Assumes last records are newest
for date in metenisweten:
    totaal_positief = metenisweten[date]['totaal_positief']

    if date in metenisweten \
       and parser.parse(date).date() <= (datetime.date.today() - datetime.timedelta(days=3))\
       and 'nu_op_ic' in metenisweten[date] and metenisweten[date]['nu_op_ic']:

        # print(str(date)+' '+str(metenisweten[date]['nu_op_ic']))
        nu_op_ic = metenisweten[date]['nu_op_ic']

    if date in metenisweten \
       and parser.parse(date).date() <= (datetime.date.today() - datetime.timedelta(days=3))\
       and 'nu_opgenomen' in metenisweten[date] and metenisweten[date]['nu_opgenomen']:

        # print(str(date)+' '+str(metenisweten[date]['nu_opgenomen']))
        nu_opgenomen = metenisweten[date]['nu_opgenomen']

    if metenisweten[date]['rivm_schatting_besmettelijk']['value']:
        geschat_ziek_nu = metenisweten[date]['rivm_schatting_besmettelijk']['value']
    if metenisweten[date]['RNA']['besmettelijk']:
        geschat_ziek_nu_rna = metenisweten[date]['RNA']['besmettelijk']
    if metenisweten[date]['rolf_besmettelijk']:
        geschat_ziek_nu_rolf = metenisweten[date]['rolf_besmettelijk']
    if metenisweten[date]['Rt_avg'] is not None:
        Rt = float(metenisweten[date]['Rt_avg'])
    # if metenisweten[date]['rivm_totaal_personen_getest'] and metenisweten[date]['rivm_totaal_personen_positief']:
    #     positief_percentage = 100 * metenisweten[date]['rivm_totaal_personen_positief'] / metenisweten[date]['rivm_totaal_personen_getest']
    if 'rivm_totaal_tests' in metenisweten[date] and 'rivm_totaal_tests_positief' in metenisweten[date]:
        positief_percentage = 100 * metenisweten[date]['rivm_totaal_tests_positief'] / metenisweten[date]['rivm_totaal_tests']
    if metenisweten[date]['besmettingleeftijd_gemiddeld']:
        gemiddeldeleeftijdarray.append(metenisweten[date]['besmettingleeftijd_gemiddeld'])

gemiddeldeleeftijdweek = int(round(sum(gemiddeldeleeftijdarray[-7:])/7))

eenopXziek = round(17500000/geschat_ziek_nu)
eenopXziekRNA = round(17500000/geschat_ziek_nu_rna)
eenopXziekRolf = round(17500000/geschat_ziek_nu_rolf)

gegenereerd_op=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
gegenereerd_datum=datetime.datetime.now().strftime("%Y-%m-%d")
gegenereerd_tijd=datetime.datetime.now().strftime("%H:%M:ss")

# Percentage gezette prikken, handmatig tot dataset beschikbaar is
prikken_gezet_perc=5.99
prikken_gezet=2097980

filename ='../cache/stats.csv'
with open(filename, 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    for row in csv_reader:
        if row[0] == 'python_lines':
            python_lines = int(row[1])
        if row[0] == 'cache_size':
            cache_size = int(row[1])*1000

substitutes = {
    'totaal_positief' : decimalstring(totaal_positief),

    'geschat_ziek_rivm' : decimalstring(geschat_ziek_nu),
    'geschat_ziek_rna' : decimalstring(round(geschat_ziek_nu_rna)),
    'geschat_ziek_rolf' : decimalstring(round(geschat_ziek_nu_rolf)),

    'ziekverhouding' : str(eenopXziek),
    'ziekverhouding_color' : 'green' if eenopXziek > 1000 else 'yellow' if eenopXziek > 500 else 'red',

    'ziekverhouding_rna' : str(eenopXziekRNA),
    'ziekverhouding_rna_color' : 'green' if eenopXziekRNA > 1000 else 'yellow' if eenopXziekRNA > 500 else 'red',

    'ziekverhouding_rolf' : str(eenopXziekRolf),
    'ziekverhouding_rolf_color' : 'green' if eenopXziekRolf > 1000 else 'yellow' if eenopXziekRolf > 500 else 'red',

    'nu_opgenomen' : decimalstring(nu_opgenomen),
    'nu_opgenomen_color': 'green' if nu_opgenomen < 500 else 'yellow' if nu_opgenomen < 1500 else 'red',

    'nu_op_ic' : decimalstring(nu_op_ic),
    'nu_op_ic_color' : 'green' if nu_op_ic < 50 else 'yellow' if nu_op_ic < 150 else 'red',

    'Rt' : decimalstring(Rt),
    'Rt_color': 'green' if Rt < 0.9 else 'yellow' if Rt < 1 else 'red',

    'positief_percentage' : decimalstring(round(positief_percentage,1))+'%',
    'positief_percentage_color' : 'green' if positief_percentage < 5 else 'yellow' if positief_percentage < 20 else 'red',

    'prikken_gezet' : decimalstring(prikken_gezet),
    'prikken_gezet_perc' : decimalstring(round(prikken_gezet_perc,2))+'%',
    'prikken_gezet_color' : 'green' if prikken_gezet_perc > 60 else 'yellow' if prikken_gezet_perc > 40 else 'red',

    'positief_leeftijd' : str(gemiddeldeleeftijdweek),

    'gegenereerd_op':       gegenereerd_op,
    'gegenereerd_op_datum': gegenereerd_datum,
    'gegenereerd_op_tijd':  gegenereerd_tijd,

    'python_lines': decimalstring(python_lines),
    'cache_size': decimalstring(cache_size)
}

def getTemplates(templatedir):
    templates = []
    for f in [f for f in listdir(templatedir) if (f.__contains__('.template.') and isfile(join(templatedir, f)))]:
        templates.append(join(templatedir, f))
    return templates

for tin in getTemplates(templatedir):
    tout = join(outputdir, basename(tin.replace('.template.','.')))
    print(tin + ' -> ' + tout)

    with open(tin, 'r') as templatefile:
        template = templatefile.read()
        
    with open(tout, 'w') as outputfile:
        outputfile.write(Template(template).substitute(substitutes))
