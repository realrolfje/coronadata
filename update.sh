git pull
./creategraphs.sh
echo "<!-- updated $(date) -->" >> docs/index.html
git add .
git commit -m 'Ran update script'
git push
