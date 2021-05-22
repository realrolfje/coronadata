mkdir -p cache

cd scripts
./createHeatmap.py
./createRtGraph.py
./createRNAGraph.py
./calculateDailyExcelData.py
./createCovidTestsGraph.py
./createZiekGraph.py
./createZiekGraph.py sliding
./createZiekenhuisTotaalGraph.py
./createSchattingAfwijkingGraph.py
./createLiveIcon.py
./createTestGraph.py
./createMobilityGraph.py
./createVaccinGraph.py
./processEventsList.py
./updatePageHits.py
./createPageHitsGraph.py

rm ../cache/stats.csv
lines=$(find . -name "*.py" | xargs cat | wc -l | awk '{print $1;}')
echo "python_lines;$lines" > ../cache/stats.csv
cachesize=$(du -sk ../cache | awk '{print $1;}')
echo "cache_size;$cachesize" >> ../cache/stats.csv

cd prikafspraak
./prikafspraak.sh
cd ..

./processTemplates.py
cd ..
