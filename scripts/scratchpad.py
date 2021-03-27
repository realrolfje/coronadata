#!/usr/bin/env python3
#

import time
import os
import urllib.request
import datetime
from dateutil import parser
import pytz

def downfresh(filename, url):
    timezone = pytz.timezone("Europe/Amsterdam")

    if os.path.isfile(filename):
        lastdownload = datetime.datetime.fromtimestamp(os.stat(filename).st_mtime, tz=timezone)
    else:        
        lastdownload = datetime.datetime.fromtimestamp(0,tz=timezone)

    if lastdownload > (datetime.datetime.now(tz=timezone) - datetime.timedelta(hours = 1)):
        # If just downloaded, don't bother checking with the server
        # print("Just downloaded, don't check the server")
        return False

    with urllib.request.urlopen(url) as response:
        meta = response.headers
        lastmodified = parser.parse(meta['Last-Modified'])
        charset = meta.get_content_charset() or 'utf-8'
        # print('last download: '+str(lastdownload))
        # print('last modified: '+str(lastmodified))

        if (lastmodified > lastdownload) or (os.path.getsize(filename) < 10):
            print("Downloading fresh data to "+filename)
            with open(filename, 'w') as f:
                f.write(
                    response.read().decode(charset)
                )
            return True
        else:
            # print("Not modified, no need to download")
            return False

downfresh(
        '../cache/COVID-19_rioolwaterdata.json',
        'https://data.rivm.nl/covid-19/COVID-19_rioolwaterdata.json'
)
