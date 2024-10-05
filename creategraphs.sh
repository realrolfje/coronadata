mkdir -p cache
rm -f cache/errors.log

# Workaround for strange download problem variants
# rm -f cache/COVID-19_varianten.json

cd scripts

# new combined graphs processing
./createGraphs.py
./createGraphs.py 365

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
