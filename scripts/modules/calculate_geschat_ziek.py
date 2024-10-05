#!/usr/bin/env python3
#
# Calculates the average number of sick people.
#
from metenisweten import metenisweten
from datecache import dateCache
from scipy.signal import savgol_filter
from math import log

# https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter
def smooth(inputArray):
    return double_savgol(inputArray, 2, 13, 1)


# https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter
def double_savgol(inputArray, iterations, window, order):
    outputArray = inputArray
    while iterations > 0:
        outputArray = savgol_filter(outputArray, window, order)
        iterations = iterations - 1
    return outputArray


def calculate():
    print("Calculate average number of ill people based on tests and rna data (magic formula)")
    dates = []
    ziek = []
    for datum, record in metenisweten.items():
        sample_size = record.get('rivm_totaal_tests' , 0) or 0
        cases = record.get('rivm_totaal_tests_positief' , 0) or 0

        if sample_size == 0: 
            # Geen samples, dan uit varianten
            for code, sample in record['varianten'].items():
                sample_size += sample.get('sample_size',0)
                cases += sample.get('cases',0)

        if sample_size == 0:
            continue

        totaal_rna = record['RNA']['totaal_RNA_per_100k'] or 0 

        if totaal_rna <= 1:
            print(f"{datum} no RNA")
            continue

        # print(f"{datum} {sample_size} -> {cases} -> {totaal_rna}")

        dates.append(datum)
        ziek.append(
            ((1000000*cases/sample_size)
                + (3 * sample_size)
                + (22 * cases))
            * log(totaal_rna, 10)
            / 44
        )

    ziek = smooth(ziek)
    for i in range(len(dates)):
        date = dates[i]
        metenisweten[date]['rolf_besmettelijk'] = ziek[i]


if __name__ == "__main__":
    calculate()
    dateCache.cacheReport()
