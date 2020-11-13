#!/usr/bin/env python3
#
from matplotlib import pyplot as plt
from dateutil import parser
from statistics import mean
import datetime
import csv
import json
import modules.brondata as brondata
from modules.brondata import decimalstring, smooth
from scipy.ndimage.filters import uniform_filter1d
from operator import itemgetter

#brondata.freshdata()
#riooldata = brondata.readjson('../data/COVID-19_rioolwaterdata-1-nov-2020.json')
riooldata = brondata.readjson('../cache/COVID-19_rioolwaterdata.json')

print("Date_measurement;Postal_code;Security_region_code;Security_region_name;RNA_per_ml;RNA_flow_per_100000")
for record in riooldata:
    print(str(record['Date_measurement']), end =";" )
    print(str(record['Postal_code']), end =";" )
    print(str(record['Security_region_code']), end =";" )
    print(str(record['Security_region_name']), end =";" )

    if 'RNA_per_ml' in record and record['RNA_per_ml']:
        print(str(record['RNA_per_ml']), end =";" )
    else:
        print("",end=';')

    if 'RNA_flow_per_100000' in record and record['RNA_flow_per_100000']:
        print(str(record['RNA_flow_per_100000']), end =";" )
    else:
        print(end=';')
    print()


#      {
#    "RWZI_AWZI_code": 32002,
#    "RWZI_AWZI_name": "Tilburg",
#    "X_coordinate": 132554,
#    "Y_coordinate": 401565,
#    "Postal_code": "5048TD",
#    "Security_region_code": "VR20",
#    "Security_region_name": "Midden- en West-Brabant",
#    "Percentage_in_security_region": "1",
#    "RNA_per_ml": 1837,
#    "Representative_measurement": true
#  },
