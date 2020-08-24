cd scripts
./createHeatmap.py
./createRtGraph.py
./createRNAGraph.py
./calculateDailyExcelData.py
./createGraph.py
cd ..
echo "< updated $(date) -->" >> docs/index.html
git add .
git commit -m 'Ran getDailyExcelData'
git push