#!/usr/bin/env python3
#
# pip3 install matplotlib

import sys
import modules.brondata as brondata
from modules.datautil import runIfNewData

# Graphs
from createRtGraph import createRtraph
from createVariantenGraph import createVariantenGraph

def main():
    runIfNewData(__file__)
    metenisweten = brondata.readjson('../cache/daily-stats.json')
    varianten = brondata.readjson('../cache/COVID-19_varianten.json')
    
    createRtraph(metenisweten)
    createVariantenGraph(metenisweten, varianten)

if __name__ == '__main__':
    sys.exit(main())