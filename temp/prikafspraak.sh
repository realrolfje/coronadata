#!/bin/bash
#
# Send a telegram message for the age group that can make online appointments
#

counter=$(($(cat counter.txt) + 5))

while [ $counter -ge 1950 ]
do
  url="https://user-api.coronatest.nl/vaccinatie/programma/bepaalbaar/$counter/NEE/NEE"
  kanik=$(curl -s $url)
  
  if [[ "$kanik" == *"true"* ]]; then
    echo "$counter" > counter.txt
    text="Online een afspraak maken kan voor mensen die geboren zijn in $counter of eerder."
    curl -d "$text" -H "Content-type: text/plain" -X POST http://noderedpi.local:1880/alert
    exit 0
  fi
  ((counter--))
done
