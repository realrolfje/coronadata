#!/usr/bin/env python3
#
import urllib.request
import re 
from datetime import datetime

url="https://hitcounter.pythonanywhere.com/count/tag.svg?url=https%3A%2F%2Frealrolfje.github.io%2Fcoronadata%2F"

with urllib.request.urlopen(url) as response:
    body = str(response.read())
    counter=re.search('>[\.,0-9]+</', body).group(0)[1:-2]
    date=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    print("https://realrolfje.github.io/coronadata/ has "+counter+" total pagehits.")

filename="../data/pagehits.csv"
with open(filename, "a") as file_object:
    file_object.write(date+';'+counter+'\n')