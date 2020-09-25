git pull
mkdir -p cache
cd scripts
./createHeatmap.py
./createRtGraph.py
./createRNAGraph.py
./calculateDailyExcelData.py
./createZiekGraph.py
cd ..
open graphs
