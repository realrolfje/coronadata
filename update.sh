cd scripts
./calculateDailyExcelData.py
./createGraph.py
./createHeatmap.py
cd ..
git add .
git commit -m 'Ran getDailyExcelData'
git push