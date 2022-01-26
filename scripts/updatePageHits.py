#!/usr/bin/env python3
#
import urllib.request
from urllib.error import URLError, HTTPError
import re 
from datetime import datetime
from modules.brondata import logError


# The source of the hit counter at pythonanywhere and blakedrumm is:
# https://github.com/brentvollebregt/hit-counter
#
# The svg returned is:
#
# <?xml version="1.0"?>
# <svg xmlns="http://www.w3.org/2000/svg" width="80" height="20">
# <rect width="30" height="20" fill="#555"/>
# <rect x="30" width="50" height="20" fill="#4c1"/>
# <rect rx="3" width="80" height="20" fill="transparent"/>
# 	<g fill="#fff" text-anchor="middle"
#     font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
# 	    <text x="15" y="14">hits</text>
# 	    <text x="55" y="14">2045</text>
# 	</g>
# <!-- This count is for the url: realrolfje.github.io/coronadata/ -->
# </svg>
#

#  <img src="https://counter.blakedrumm.com/count/tag.svg?url=https%3A%2F%2Frealrolfje.github.io%2Fcoronadata%2F" alt="Hits">
url="https://counter.blakedrumm.com/count/tag.svg?url=https%3A%2F%2Frealrolfje.github.io%2Fcoronadata%2F"


try:
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    headers = {'User-Agent': user_agent}
    req = urllib.request.Request(url=url, headers=headers)

    with urllib.request.urlopen(req) as response:
        body = str(response.read())
        counter=re.search('>[\.,0-9]+</', body).group(0)[1:-2]
        date=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        print("https://realrolfje.github.io/coronadata/ has "+counter+" total pagehits.")

    filename="../data/pagehits.csv"
    with open(filename, "a") as file_object:
        file_object.write(date+';'+counter+'\n')

except HTTPError as e:
    logError("Problem opening '%s': http error %d, %s" % (url, e.code, e.reason))
except URLError as e:
    logError("Problem opening '%s': %s" % (url, e.reason))
