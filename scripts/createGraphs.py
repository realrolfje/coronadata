#!/usr/bin/env python3
#
# pip3 install matplotlib

import sys
import modules.brondata as brondata
from modules.datautil import runIfNewData

# Graphs
from createRtGraph import createRtraph
from createVariantenGraph import createVariantenGraph
from createVaccinGraph import createVaccinGraph
from createRNAGraph import createRNAGraph
from createHeatmap import createHeatmap
from createZiekGraph import createZiekGraph
from createCovidTestsGraph import createCovidTestsGraph

def main():
    runIfNewData(__file__)
    metenisweten = brondata.readjson('../cache/daily-stats.json')
    varianten = brondata.readjson('../cache/COVID-19_varianten.json')
    events = brondata.readjson('../data/measures-events.json')
    
    createRtraph(metenisweten)
    createVariantenGraph(metenisweten, varianten)
    createVaccinGraph(metenisweten, events)
    createRNAGraph(metenisweten)
    createHeatmap(metenisweten, events)
    createZiekGraph(metenisweten, events)
    createCovidTestsGraph(metenisweten, events)

if __name__ == '__main__':
    sys.exit(main())