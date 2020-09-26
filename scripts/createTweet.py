#!/usr/bin/env python3
#

import modules.brondata as brondata

brondata.freshdata()
metenisweten = brondata.readjson('../cache/daily-stats.json')

for date in metenisweten:
    totaal_positief = metenisweten[date]['totaal_positief']
    nu_op_ic = metenisweten[date]['nu_op_ic']
    if metenisweten[date]['rivm_schatting_besmettelijk']['value']:
        geschat_ziek_nu = metenisweten[date]['rivm_schatting_besmettelijk']['value']

def decimalstring(number):
    return "{:,}".format(number).replace(',','.')

print('Write text for tweet update in ../docs/tweet.txt')
with open("../docs/tweet.txt", 'w') as file:
    file.write(
        'Positief getest: '+decimalstring(totaal_positief)+' (RIVM).\n' +
        'Nu op IC: '+decimalstring(nu_op_ic)+' (NICE).\n' +
        '1 op '+str(round(17500000/geschat_ziek_nu))+' mensen is nu ziek/besmettelijk.\n'
        'https://realrolfje.github.io/coronadata/\n' +
        '#COVID19 #coronavirus'
    )
