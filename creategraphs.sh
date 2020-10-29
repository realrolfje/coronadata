mkdir -p cache
cd scripts
./createHeatmap.py
./createRtGraph.py
./createRNAGraph.py
./calculateDailyExcelData.py
./createCovidTestsGraph.py
./createZiekGraph.py
./processTemplates.py
./createSchattingAfwijkingGraph.py
./createLiveIcon.py
./createTestGraph.py
./createMobilityGraph.py
cd ..
