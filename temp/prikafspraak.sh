#!/bin/bash
#
# Send a telegram message for the age group that can make online appointments
#

counter=$(cat ../scripts/prikafspraak/geboortejaar.txt)
text="Online een corona vaccinatie afspraak maken kan voor mensen die geboren zijn in $counter of eerder. https://coronatest.nl/ik-wil-me-laten-vaccineren/een-online-afspraak-maken"
curl -d "$text" -H "Content-type: text/plain" -X POST http://noderedpi.local:1880/alert
