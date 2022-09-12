mkdir -p cache
rm -f cache/errors.log

cd scripts

# new combined graphs processing
./createGraphs.py
./createGraphs.py 365

./createHeatmap.py
# ./createRtGraph.py
./createRNAGraph.py
./createCovidTestsGraph.py
./createZiekGraph.py
# ./createMobilityGraph.py
# ./createVaccinGraph.py
# ./createVariantenGraph.py

./createHeatmap.py 365
# ./createRtGraph.py 365
./createRNAGraph.py 365
./createCovidTestsGraph.py 365
./createZiekGraph.py 365
# ./createMobilityGraph.py 365
# ./createVaccinGraph.py 365
# ./createVariantenGraph.py 365

./calculateDailyExcelData.py
./createZiekenhuisTotaalGraph.py
./createSchattingAfwijkingGraph.py
./createLiveIcon.py
./createTestGraph.py
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
