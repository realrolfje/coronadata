#!/bin/bash
#
# Welk geboortejaar zonder medische indicatie kan een afspraak maken?
#

file="geboortejaar.txt"
huidig=$(cat $file)
counter=$(($huidig + 5))

if test `find "$file" -mmin +240`
then
  while [ $counter -ge $huidig ]
  do
    url="https://user-api.coronatest.nl/vaccinatie/programma/bepaalbaar/$counter/NEE/NEE"
    kanik=$(curl -s $url)
    
    if [[ "$kanik" == *"true"* ]]; then
      echo "Online een corona vaccinatie afspraak maken kan voor geboortejaar $counter."
      echo "$counter" > $file
      exit 0
    fi
    ((counter--))
  done
else
  echo "Geen nieuwe vaccinatiesite scan gedaan. Geboortejaar is $huidig."
fi


