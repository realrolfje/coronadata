cd scripts
./createHeatmap.py
./createRtGraph.py
./createRNAGraph.py
./calculateDailyExcelData.py
./createGraph.py
cd ..
git add .
git commit -m 'Ran getDailyExcelData'
git push