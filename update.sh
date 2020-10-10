git pull
mkdir -p cache
cd scripts
./createHeatmap.py
./createRtGraph.py
./createRNAGraph.py
./calculateDailyExcelData.py
./createCovidTestsGraph.py
./createZiekGraph.py
./processTemplates.py
cd ..
echo "<!-- updated $(date) -->" >> docs/index.html
git add .
git commit -m 'Ran update script'
git push
