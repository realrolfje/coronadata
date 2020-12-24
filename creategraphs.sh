mkdir -p cache
cd scripts
./createHeatmap.py
./createRtGraph.py
./createRNAGraph.py
./calculateDailyExcelData.py
./createCovidTestsGraph.py
./createZiekGraph.py
./createZiekGraph.py sliding
./createSchattingAfwijkingGraph.py
./createLiveIcon.py
./createTestGraph.py
./createMobilityGraph.py
./processTemplates.py
./processEventsList.py
./updatePageHits.py
./createPageHitsGraph.py
cd ..
lines=$(find . -name "*.py" | xargs cat | wc -l)
echo "Total $lines lines of python code"

