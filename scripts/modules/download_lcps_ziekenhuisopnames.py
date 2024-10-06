#!/usr/bin/env python3
#
# Downloads the LCPS dataset containing intensive care and hospital intake.
#
# Please note that these files are no longer updates since April 2024

# https://lcps.nu/wp-content/uploads/covid-19-datafeed.csv
# 0 datum: datum waarop de gegevens zijn vastgesteld, geschreven met datumnotatie dd-mm-jjjj (bijvoorbeeld 01-01-2020).
# 1 IC_capaciteit_totaal: de totale IC-capaciteit bestaande uit bezette bedden, BOSS-capaciteit en vrije capaciteit.
# 2 kliniek_capaciteit_totaal: de totale kliniekcapaciteit bestaande uit bezette bedden en vrije capaciteit.
# 3 IC_bezetting_covid: het aantal IC-bedden bezet door patiënten met COVID-19 in Nederland.
# 4 IC_bezetting_covid_internationaal: het aantal IC-bedden in het buitenland bezet door uit Nederland verplaatste patiënten met COVID-19.
# 5 IC_bezetting_ontlabeld: het aantal IC-bedden bezet door patiënten die met COVID-19 in het ziekenhuis zijnopgenomen maar niet langer besmettelijk zijn. Een ontlabelde patiënt hoeft daarom niet meer op een COVID-bed te liggen. Deze kolom is vanaf 12 december 2022 vrijblijvend en deze bedden worden anders als noncovid bedden geteld.
# 6 IC_bezetting_noncovid: het aantal IC-bedden bezet door patiënten zonder COVID-19 in Nederland.
# 7 kliniek_bezetting_covid: het aantal kliniekbedden bezet door patiënten met COVID-19 in Nederland.
# 8 kliniek_bezetting_ontlabeld: het aantal kliniekbedden bezet door patiënten die met COVID in het ziekenhuis is opgenomen, maar niet langer besmettelijk zijn. Een ontlabelde patiënt hoeft daarom niet meer op een COVID-bed te liggen. Deze kolom is vanaf 12 december 2022 vrijblijvend en deze bedden worden anders als noncovid bedden geteld.
# 9 kliniek_bezetting_noncovid: het aantal kliniekbedden bezet door patiënten zonder COVID-19 in Nederland.
# 10 IC_opnames_covid: het aantal patiënten met COVID-19 dat de afgelopen 24 uur nieuw is opgenomen op de IC in Nederland. (intake)
# 11 kliniek_opnames_covid: het aantal patiënten met COVID-19 dat de afgelopen 24 uur nieuw is opgenomen in de kliniek in Nederland (intake)
#

import os
import csv
from utilities import downloadIfStale, readjson
from defaults import cachedir
from metenisweten import initrecord
from datecache import dateCache



def download_lcps_datafeed(force=False) -> str:
    filename = os.path.join(cachedir, "covid-19-datafeed.csv")
    if downloadIfStale(
        filename=filename,
        url="https://lcps.nu/wp-content/uploads/covid-19-datafeed.csv",
        force = force):
        return filename
    else:
        return None


def store_datafeed(filename) -> bool:
    if filename == None:
        return False
    print("Add lcps IC and hospitalization data")
    with open(filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0 
        for row in csv_reader:
            if line_count > 0: # skip header
                datum = dateCache.sanitizeDate(row[0]) # Because idiots don't understand ISO date
                ic_bezetting_covid = row[3]
                kliniek_bezetting_covid = row[7]

                m = initrecord(datum)
                m['nu_op_ic'] = ic_bezetting_covid
                m['nu_opgenomen'] = kliniek_bezetting_covid
        
            line_count = line_count + 1

    return True


def process(force=False) -> bool:
    """Download and process the data"""
    return store_datafeed(download_lcps_datafeed(force))


if __name__ == "__main__":
    process(force=True)
    dateCache.cacheReport()
