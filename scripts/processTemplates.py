#!/usr/bin/env python3
#
import modules.brondata as brondata
import datetime
from string import Template
from dateutil import parser
from os import listdir
from os.path import isfile, join, basename

templatedir = '../docs/templates'
outputdir = '../docs'

brondata.freshdata()
metenisweten = brondata.readjson('../cache/daily-stats.json')

gemiddeldeleeftijdarray=[]
# Assumes last records are newest
for date in metenisweten:
    totaal_positief = metenisweten[date]['totaal_positief']
    nu_op_ic = metenisweten[date]['nu_op_ic']
    nu_opgenomen = metenisweten[date]['nu_opgenomen']
    if metenisweten[date]['rivm_schatting_besmettelijk']['value']:
        geschat_ziek_nu = metenisweten[date]['rivm_schatting_besmettelijk']['value']
    if metenisweten[date]['Rt_avg'] is not None:
        Rt = metenisweten[date]['Rt_avg']
    if metenisweten[date]['rivm_totaal_tests'] and metenisweten[date]['positief'] and parser.parse(date).date() <= (datetime.date.today() - datetime.timedelta(days=11)):
        positief_percentage = 100 * metenisweten[date]['positief'] / metenisweten[date]['rivm_totaal_tests']

#    gemiddeldeleeftijdarray.append(gemiddeld)



def decimalstring(number):
    return "{:,}".format(number).replace(',','.')

eenopXziek = round(17500000/geschat_ziek_nu)

substitutes = {
    'totaal_positief' : decimalstring(totaal_positief),

    'ziekverhouding' : '1:'+str(eenopXziek),
    'ziekverhouding_color' : 'green' if eenopXziek > 1000 else 'yellow' if eenopXziek > 500 else 'red',

    'nu_opgenomen' : decimalstring(nu_opgenomen),
    'nu_opgenomen_color': 'green' if nu_opgenomen < 500 else 'yellow' if nu_opgenomen < 1500 else 'red',

    'nu_op_ic' : decimalstring(nu_op_ic),
    'nu_op_ic_color' : 'green' if nu_op_ic < 50 else 'yellow' if nu_op_ic < 150 else 'red',

    'Rt' : decimalstring(Rt),
    'Rt_color': 'green' if Rt < 0.9 else 'yellow' if Rt < 1 else 'red',

    'positief_percentage' : decimalstring(round(positief_percentage,1))+'%',
    'positief_percentage_color' : 'green' if positief_percentage < 5 else 'yellow' if positief_percentage < 20 else 'red'   
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
