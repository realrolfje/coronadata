git pull
mkdir -p cache
cd scripts
./createHeatmap.py
./createRtGraph.py
./createRNAGraph.py
./calculateDailyExcelData.py
./createCovidTestsGraph.py
./createZiekGraph.py
./createTweet.py
./processTemplates.py
cd ..
open docs/index.html
