#!/usr/bin/env python3
#
import modules.brondata as brondata
import sys


def main():
    # runIfNewData(__file__)
    # metenisweten = brondata.readjson('../data/daily-stats.json')
    # varianten = brondata.readjson('../cache/COVID-19_varianten.json')
    createVariantenTree()

def buildVarianten():
    varianten = brondata.readjson('../cache/COVID-19_varianten.json')
    namefix = {
        "Omicron" : "Omikron"
    }

    # Get all id's and names of the variants and put them in variantcodes
    variantcodes = {}
    for record in varianten:
        code = record['Variant_code']
        name = record['Variant_name']
        if code not in variantcodes:
            if name == '':
                variantcodes[code] = {"name": code}
            elif name in namefix:
                variantcodes[code] = {"name": "%s (%s)" % (namefix[name], code)}
            else:
                variantcodes[code] = {"name": "%s (%s)" % (name, code)}

            variantcodes[code]['subvariant_of'] = record['Is_subvariant_of']
    return variantcodes

def printVariantenTree(varianten):

    def printRecurse(depth, code):
        print("%s%s" % ("   "*depth, code))
        for c2 in varianten:
            if varianten[c2]['subvariant_of'] == code:
                printRecurse(depth+1, c2)

    for code in varianten:
        if len(varianten[code]['subvariant_of']) == 0:
            printRecurse(0, code)


def createVariantenTree():
    variantcodes = buildVarianten()
    printVariantenTree(variantcodes)

if __name__ == '__main__':
    sys.exit(main())