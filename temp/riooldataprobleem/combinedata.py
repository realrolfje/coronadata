#!/usr/bin/env python3
#

# This is a hack to get the brondata modules
import sys
sys.path.append('../../scripts')

from dateutil import parser
import csv
import json
import modules.brondata as brondata
from modules.brondata import decimalstring, smooth
from scipy.ndimage.filters import uniform_filter1d
from operator import itemgetter

#brondata.freshdata()
veiligheidsregios = brondata.readjson('../../data/veiligheidsregios.json')
riooldataoud = brondata.readjson('COVID-19_rioolwaterdata-1-nov-2020.json')
riooldatanieuw = brondata.readjson('COVID-19_rioolwaterdata.json')

riooldatacombi = []

for oudrecord in riooldataoud:
    if oudrecord['Date_measurement'] > '2020-09-01':
        for nieuwrecord in riooldatanieuw:
            if (
                oudrecord['Date_measurement'] > '2020-09-01' and
                oudrecord['Date_measurement'] == nieuwrecord['Date_measurement'] and
                oudrecord['Postal_code'] == nieuwrecord['Postal_code'] and
                oudrecord['Security_region_code'] == nieuwrecord['Security_region_code'] and
                oudrecord['RWZI_AWZI_code'] == nieuwrecord['RWZI_AWZI_code'] and
                'RNA_per_ml' in oudrecord and oudrecord['RNA_per_ml'] and 
                'RNA_flow_per_100000' in nieuwrecord and nieuwrecord['RNA_flow_per_100000']
            ):
                riooldatacombi.append({
                    'Date_measurement': oudrecord['Date_measurement'],
                    'Postal_code': oudrecord['Postal_code'],
                    'Security_region_code': oudrecord['Security_region_code'],
                    'Security_region_name': oudrecord['Security_region_name'],
                    'RWZI_AWZI_code': oudrecord['RWZI_AWZI_code'],
                    'RNA_per_ml': oudrecord['RNA_per_ml'],
                    'RNA_flow_per_100000': nieuwrecord['RNA_flow_per_100000'],
                    'Percentage_in_security_region': oudrecord['Percentage_in_security_region'],
                    'inwoners': veiligheidsregios[oudrecord['Security_region_code']]['inwoners']
                })

print("Date_measurement;Postal_code;Security_region_code;Security_region_name;Percentage_in_security_region;inwoners;RNA_per_ml;RNA_flow_per_100000")
for record in riooldatacombi:
    print(str(record['Date_measurement']), end =";" )
    print(str(record['Postal_code']), end =";" )
    print(str(record['Security_region_code']), end =";" )
    print(str(record['Security_region_name']), end =";" )
    print(str(record['Percentage_in_security_region']), end =";" )
    print(str(record['inwoners']), end =";" )

    if 'RNA_per_ml' in record and record['RNA_per_ml']:
        print(str(record['RNA_per_ml']), end =";" )
    else:
        print("",end=';')

    if 'RNA_flow_per_100000' in record and record['RNA_flow_per_100000']:
        print(str(record['RNA_flow_per_100000']), end =";" )
    else:
        print(end=';')
    print()
