#!/usr/bin/env python3
#
import modules.arguments as arguments
import modules.brondata as brondata
from modules.brondata import decimalstring, dateCache
import datetime
from string import Template
from os import listdir
from os.path import isfile, join, basename
import csv
from modules.datautil import runIfNewData

runIfNewData(__file__)

templatedir = '../docs/templates'
outputdir = '../docs'

metenisweten = brondata.readjson('../data/daily-stats.json')

dates=[]

gemiddeldeleeftijdarray=[]
# Assumes last records are newest
for date in metenisweten:
    dates.append(date)

    totaal_positief = metenisweten[date]['totaal_positief']
    totaal_positief_datum = date

    if date in metenisweten \
       and dateCache.parse(date).date() <= (dateCache.today() - datetime.timedelta(days=3))\
       and 'nu_op_ic' in metenisweten[date] and metenisweten[date]['nu_op_ic']:

        # print(str(date)+' '+str(metenisweten[date]['nu_op_ic']))
        nu_op_ic = metenisweten[date]['nu_op_ic']
        nu_op_ic_datum = date

    if date in metenisweten \
       and dateCache.parse(date).date() <= (dateCache.today() - datetime.timedelta(days=3))\
       and 'nu_opgenomen' in metenisweten[date] and metenisweten[date]['nu_opgenomen']:

        # print(str(date)+' '+str(metenisweten[date]['nu_opgenomen']))
        nu_opgenomen = metenisweten[date]['nu_opgenomen']
        nu_opgenomen_datum = date

    if metenisweten[date]['rivm_schatting_besmettelijk']['value']:
        geschat_ziek_nu = metenisweten[date]['rivm_schatting_besmettelijk']['value']
        geschat_ziek_nu_datum = date

    if metenisweten[date]['RNA']['RNA_per_100k_avg']:
        rna_per_100k = metenisweten[date]['RNA']['RNA_per_100k_avg']
        rna_per_100k_datum = date
    if metenisweten[date]['RNA']['besmettelijk']:
        geschat_ziek_nu_rna = metenisweten[date]['RNA']['besmettelijk']
        geschat_ziek_nu_rna_datum = date
    if metenisweten[date]['rolf_besmettelijk']:
        geschat_ziek_nu_rolf = metenisweten[date]['rolf_besmettelijk']
        geschat_ziek_nu_rolf_datum = date
    if metenisweten[date]['Rt_avg'] is not None:
        Rt = float(metenisweten[date]['Rt_avg'])
        Rt_datum = date
        
    # if metenisweten[date]['rivm_totaal_personen_getest'] and metenisweten[date]['rivm_totaal_personen_positief']:
    #     positief_percentage = 100 * metenisweten[date]['rivm_totaal_personen_positief'] / metenisweten[date]['rivm_totaal_personen_getest']
    if 'rivm_totaal_tests' in metenisweten[date] and 'rivm_totaal_tests_positief' in metenisweten[date]:
        positief_getest = metenisweten[date]['rivm_totaal_tests_positief']
        vandaag_getest = metenisweten[date]['rivm_totaal_tests']
        positief_percentage = 100 * positief_getest / vandaag_getest
        vandaag_getest_datum = date
    if metenisweten[date]['besmettingleeftijd_gemiddeld']:
        gemiddeldeleeftijdarray.append(metenisweten[date]['besmettingleeftijd_gemiddeld'])
    if metenisweten[date]['vaccinaties']['totaal']:
        prikken_gezet = metenisweten[date]['vaccinaties']['totaal']
        prikken_gezet_perc=100*(prikken_gezet/(17500000*2)) # 2 prikken per persoon!
        prikken_gezet_datum = date
    if metenisweten[date]['vaccinaties']['totaal_geschat']:
        prikken_gezet_geschat = metenisweten[date]['vaccinaties']['totaal_geschat']
        prikken_gezet_geschat_datum = date
    if metenisweten[date]['vaccinaties']['totaal_mensen_geschat']:
        totaal_mensen_geschat = metenisweten[date]['vaccinaties']['totaal_mensen_geschat']
        mensen_gevaccineerd_geschat_perc=100*(totaal_mensen_geschat/(17500000))

# Iterate dates in reverse, see https://www.askpython.com/python/array/reverse-an-array-in-python
nu_opgenomen_record_sinds = "nooit"
nu_opgenomen_record_flag = False
for date in dates[::-1]:
    # Record opgenomen in ziekenhuis
    x = metenisweten[date]['nu_opgenomen']
    if x and (abs(1-(x/nu_opgenomen)) > 0.25):
        nu_opgenomen_record_flag = True    
    if (nu_opgenomen_record_flag == True) and (x >= nu_opgenomen):
        nu_opgenomen_record_sinds = date
        break

nu_op_ic_record_sinds = "nooit"
nu_op_ic_record_flag = False
for date in dates[::-1]:
    # Record opgenomen op IC
    x = metenisweten[date]['nu_op_ic']
    if x and (abs(1-(x/nu_op_ic)) > 0.25):
        nu_op_ic_record_flag = True    
    if (nu_op_ic_record_flag == True) and (x >= nu_op_ic):
        nu_op_ic_record_sinds = date
        break

geschat_ziek_rolf_record_sinds = "nooit"
geschat_ziek_rolf_record_flag = False
for date in dates[::-1]:
    # Record geschat ziek
    x = metenisweten[date]['rolf_besmettelijk']

    if x and (abs(1-(x/geschat_ziek_nu_rolf)) > 0.25):
        geschat_ziek_rolf_record_flag = True    
    if (geschat_ziek_rolf_record_flag == True) and x and (x >= geschat_ziek_nu_rolf):
        geschat_ziek_record_sinds = date
        break


positief_percentage_record_sinds = "nooit"
positief_percentage_record_flag = False
for date in dates[::-1]:
    if 'rivm_totaal_tests' in metenisweten[date] and 'rivm_totaal_tests_positief' in metenisweten[date]:
        x = 100 * metenisweten[date]['rivm_totaal_tests_positief'] / metenisweten[date]['rivm_totaal_tests']
        if x and (abs(1-(x/positief_percentage)) > 0.25):
            positief_percentage_record_flag = True    
        if (positief_percentage_record_flag == True) and x and (x >= positief_percentage):
            positief_percentage_record_sinds = date
            break

# read errors, if there are any
errors = ''
if isfile('../cache/errors.log'):
    with open('../cache/errors.log', 'r') as file:
        errors = '<p class="highlight">Errors during processing:<br/>'
        for error in file.readlines():
            errors = '%s%s<br/>' % (errors, error)
        errors += '</p>'


# print("nu opgenomen is een record sinds %s" % nu_opgenomen_record_sinds)
# print("nu op IC is een record sinds %s" % nu_op_ic_record_sinds)
# print("geschat ziek is een record sinds %s" % geschat_ziek_rolf_record_sinds)
# print("test percentage is een record sinds %s" % positief_percentage_record_sinds)

gemiddeldeleeftijdweek = int(round(sum(gemiddeldeleeftijdarray[-7:])/7))

eenopXziek = round(17500000/geschat_ziek_nu)
eenopXziekRNA = round(17500000/geschat_ziek_nu_rna)
eenopXziekRolf = round(17500000/geschat_ziek_nu_rolf)

if errors == '':
    error_warning = ''
else:
    error_warning = 'met errors'

gegenereerd_op=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
gegenereerd_datum=datetime.datetime.now().strftime("%Y-%m-%d")
gegenereerd_tijd=datetime.datetime.now().strftime("%H:%M:ss")

with open('prikafspraak/geboortejaar.txt') as f:
    vaccingeboortejaar=f.read().rstrip()

filename ='../cache/stats.csv'
with open(filename, 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    for row in csv_reader:
        if row[0] == 'python_lines':
            python_lines = int(row[1])
        if row[0] == 'cache_size':
            cache_size = int(row[1])*1000

substitutes = {
    'totaal_positief'      : decimalstring(totaal_positief),
    'totaal_positief_num'  : totaal_positief,
    'totaal_positief_datum': totaal_positief_datum,

    'geschat_ziek_rivm'             : decimalstring(geschat_ziek_nu),
    'geschat_ziek_nu_datum'         : geschat_ziek_nu_datum,
    'geschat_ziek_rna'              : decimalstring(round(geschat_ziek_nu_rna)),
    'geschat_ziek_nu_rna_datum'     : geschat_ziek_nu_rna_datum,
    'geschat_ziek_rolf'             : decimalstring(round(geschat_ziek_nu_rolf)),
    'geschat_ziek_nu_rolf_datum'    : geschat_ziek_nu_rolf_datum,
    'geschat_ziek_rolf_record_sinds': geschat_ziek_rolf_record_sinds,

    'ziekverhouding'      : str(eenopXziek),
    'ziekverhouding_color': 'green' if eenopXziek > 1000 else 'yellow' if eenopXziek > 500 else 'red',

    'ziekverhouding_rna'      : str(eenopXziekRNA),
    'ziekverhouding_rna_color': 'green' if eenopXziekRNA > 1000 else 'yellow' if eenopXziekRNA > 500 else 'red',

    'ziekverhouding_rolf'      : str(eenopXziekRolf),
    'ziekverhouding_rolf_color': 'green' if eenopXziekRolf > 1000 else 'yellow' if eenopXziekRolf > 500 else 'red',

    'nu_opgenomen'      : decimalstring(nu_opgenomen),
    'nu_opgenomen_num'  : nu_opgenomen,
    'nu_opgenomen_datum': nu_opgenomen_datum,
    'nu_opgenomen_color': 'green' if nu_opgenomen < 500 else 'yellow' if nu_opgenomen < 1500 else 'red',
    'nu_opgenomen_record_sinds' : nu_opgenomen_record_sinds,

    'nu_op_ic'      : decimalstring(nu_op_ic),
    'nu_op_ic_num'  : nu_op_ic,
    'nu_op_ic_datum': nu_op_ic_datum,
    'nu_op_ic_color': 'green' if nu_op_ic < 50 else 'yellow' if nu_op_ic < 150 else 'red',
    'nu_op_ic_record_sinds': nu_op_ic_record_sinds,

    'nu_in_ziekenhuis'     : decimalstring(nu_opgenomen + nu_op_ic),
    'nu_in_ziekenhuis_num' : nu_opgenomen + nu_op_ic,

    'rna_per_100k'       : decimalstring(round(rna_per_100k)),
    'rna_per_100k_num'   : rna_per_100k,
    'rna_per_100k_datum' : rna_per_100k_datum,

    'Rt'      : decimalstring(Rt),
    'Rt_num'  : Rt,
    'Rt_datum': Rt_datum,
    'Rt_color': 'green' if Rt < 0.9 else 'yellow' if Rt < 1 else 'red',

    'vandaag_getest'                   : decimalstring(vandaag_getest),
    'vandaag_getest_datum'             : vandaag_getest_datum,
    'positief_getest'                  : decimalstring(positief_getest),
    'positief_percentage'              : decimalstring(round(positief_percentage,1))+'%',
    'positief_percentage_num'          : round(positief_percentage,1),
    'positief_percentage_color'        : 'green' if positief_percentage < 5 else 'yellow' if positief_percentage < 20 else 'red',
    'positief_percentage_record_sinds' : positief_percentage_record_sinds,

    'prikken_gezet'      : decimalstring(prikken_gezet),
    'prikken_gezet_datum': prikken_gezet_datum,
    'prikken_gezet_perc' : decimalstring(round(prikken_gezet_perc,2))+'%',
    'prikken_gezet_color': 'green' if prikken_gezet_perc > 60 else 'yellow' if prikken_gezet_perc > 40 else 'red',

    'prikken_gezet_geschat'         : decimalstring(prikken_gezet_geschat),
    'prikken_gezet_geschat_num'     : prikken_gezet_geschat,
    'prikken_gezet_geschat_datum'   : prikken_gezet_geschat_datum,
    'prikken_gezet_geschat_perc'    : decimalstring(round(mensen_gevaccineerd_geschat_perc,2))+'%',
    'prikken_gezet_geschat_perc_num': round(mensen_gevaccineerd_geschat_perc,2),
    'prikken_gezet_geschat_color'   : 'green' if mensen_gevaccineerd_geschat_perc > 60 else 'yellow' if mensen_gevaccineerd_geschat_perc > 40 else 'red',
    'vaccingeboortejaar'            : vaccingeboortejaar, 

    'positief_leeftijd' : str(gemiddeldeleeftijdweek),

    'gegenereerd_op'      : gegenereerd_op,
    'gegenereerd_op_datum': gegenereerd_datum,
    'gegenereerd_op_tijd' : gegenereerd_tijd,

    'python_lines': decimalstring(python_lines),
    'cache_size'  : decimalstring(cache_size),

    'errors'       : errors,
    'error_warning': error_warning
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

dateCache.cacheReport()