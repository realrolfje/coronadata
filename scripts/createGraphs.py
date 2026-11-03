#!/usr/bin/env python3
#
# pip3 install matplotlib

import os
import sys
import modules.brondata as brondata
from modules.defaults import CACHE_DIR, DATA_DIR
from modules.datautil import runIfNewData

# Non-graphs, icons
from createLiveIcon                import createLiveIcon
from processEventsList             import processEventsList

# Graphs
from createRtGraph                 import createRtraph
from createVariantenGraph          import createVariantenGraph
# from createVaccinGraph             import createVaccinGraph
from createRNAGraph                import createRNAGraph
from createHeatmap                 import createHeatmap
from createZiekGraph               import createZiekGraph
from createCovidTestsGraph         import createCovidTestsGraph
from createZiekenhuisTotaalGraph   import createZiekenhuisTotaalGraph
from createSchattingAfwijkingGraph import createSchattingAfwijkingGraph
from createTestGraph               import createTestGraph
from createSariGraph               import createSariGraph
from createLaboratoriumGraph       import createLaboratoriumGraph


def main():
    runIfNewData(__file__)
    metenisweten = brondata.readjson(DATA_DIR / 'daily-stats.json')
    varianten    = brondata.readjson(CACHE_DIR / 'COVID-19_varianten.json')
    events       = brondata.readjson(DATA_DIR / 'measures-events.json')
    testpunten   = brondata.readjson(CACHE_DIR / 'testlocaties.json')

    print("Creating Rt graph")
    createRtraph(metenisweten)

    print("Creating Varianten graph")
    createVariantenGraph(metenisweten, varianten)

    # createVaccinGraph(metenisweten, events)
    print("Creating RNA graph")
    createRNAGraph(metenisweten)


    print("Creating heatmap")
    createHeatmap(metenisweten, events)

    print("Creating Ziekgraph")
    createZiekGraph(metenisweten, events)

    print("Creating SARI graph")
    createSariGraph(metenisweten)

    print("Creating laboratorium graph")
    createLaboratoriumGraph(metenisweten, events)

    print("Creating Testgraph")
    createCovidTestsGraph(metenisweten, events)

    print("Creating Live icon")
    createLiveIcon(metenisweten)

    print("Create ziekenhuis totaal graph")
    createZiekenhuisTotaalGraph(metenisweten)

    print("Create Schatting afwijkingen graph")
    createSchattingAfwijkingGraph(metenisweten)

    print("Create Test graph")
    createTestGraph(metenisweten)

    print("Process events list")
    processEventsList(events)

if __name__ == '__main__':
    sys.exit(main())
