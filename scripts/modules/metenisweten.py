import os

from defaults import datadir
from utilities import readjson, writejson, sortDictOnKey

metenisweten_file = os.path.join(datadir,'daily-stats.json')
metenisweten = readjson(metenisweten_file)

def getrecord(date):
    """Gets a record if it exists, or None if it does not"""
    return metenisweten.get(date)

def writeMetenIsWeten():
    writejson(metenisweten_file,  sortDictOnKey(metenisweten))


def initrecord(date):
    """Gets the record for the given date, or initializes a new one if it does not exist"""
    record = getrecord(date)
    if record is None:
        record = {
            'positief': 0,
            'totaal_positief': 0,
            'nu_op_ic': None,
            'nu_op_ic_lcps': None,
            'nu_op_ic_noncovid_lcps': None,
            'geweest_op_ic': 0,
            'opgenomen': 0,
            'nu_opgenomen': 0,
            'nu_opgenomen_lcps': None,
            'totaal_opgenomen': 0,
            'overleden': 0,
            'totaal_overleden': 0,
            'rivm-datum': None,
            'Rt_avg': None,
            'Rt_low': None,
            'Rt_up': None,
            'Rt_population': None,
            'RNA': {
                'totaal_RNA_per_100k': 0,
                'totaal_RNA_metingen': 0,
                'RNA_per_100k_avg': 0,
                'besmettelijk': None,  # Aantal besmettelijke mensen op basis van RNA_avg
                'besmettelijk_error': None,
                'populatie_dekking': None,
                'regio': {
                    # This will contain data per veiligheidsregio:
                    # 'VR01' : {
                    #     'totaal_RNA_per_100k'  : 0,
                    #     'totaal_RNA_metingen'  : 0,
                    #     'RNA_per_100k_avg'     : 0,
                    #     'inwoners'             : 0,
                    #     'oppervlakte'          : 0
                    # }
                }
            },
            'rivm_totaal_tests         ': None,
            'rivm_totaal_tests_positief': None,
            'rivm_totaal_personen_getest': None,
            'rivm_totaal_personen_positief': None,
            'rivm_aantal_testlabs': None,
            'rivm_infectieradar_perc': None,
            'rivm_schatting_besmettelijk': {
                'min': None,  # Minimaal personen besmettelijk
                'value': None,  # Geschat personen besmettelijk
                'max': None  # Maximaal personen besmettelijk
            },
            'besmettingleeftijd_gemiddeld': None,
            'besmettingleeftijd': {
                # key = leeftijdscategorie
                # value = aantal besmettingen
            },
            'mobiliteit': {
                'lopen': None,
                'ov': None,
                'rijden': None
            },
            'vaccinaties': {
                'astra_zeneca': None,
                'pfizer': None,
                'cure_vac': None,
                'janssen': None,
                'moderna': None,
                'sanofi': None,
                'totaal': None,
                'totaal_mensen': None,
                'totaal_geschat': None,
                'totaal_mensen_geschat': None,
                'geleverd': None,
            },
            # Besmettelijke mensen op basis van gecombineerde meetwaarden
            'rolf_besmettelijk': None,
            'varianten': {
                # Example:
                # 'B.1.525' : {
                #     'name'                 : '',
                #     'ECDC_category'        : 'DEV',
                #     'WHO_category'         : 'VUM',
                #     'includes_old_samples' : False,
                #     'Sample_size'          : 1593,
                #     'cases'                : 4
                # }
            }
        }    
        metenisweten[date] = record
    return record