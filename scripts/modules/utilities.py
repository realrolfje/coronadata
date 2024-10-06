import os
import json
import urllib.request
from urllib.error import URLError, HTTPError
import datetime
import time
from operator import itemgetter
from tqdm import tqdm
import sys


from defaults import timezone, cachedir

def downloadBinaryIfStale(filename, url):
    return downloadIfStale(filename, url, True)


def downloadIfStale(filename, url, binary=False, force=False):
    """Downloads from the given url, and writes to the given filename.
    downloadIfStale("somedata.json", "https://example.com/dataset_with_different_name.json")
    Writes a somedata.json file filled with whatever it got from the url.
    Use to download json.
    Use "binary=True" if the file needs to be binary (no character set conversion)
    """
    filename = os.path.realpath(filename)
    if os.path.isfile(filename):
        lastdownload = datetime.datetime.fromtimestamp(
            os.stat(filename).st_mtime, tz=timezone)
    else:
        lastdownload = datetime.datetime.fromtimestamp(0, tz=timezone)

    if (not force) and lastdownload > (datetime.datetime.now(tz=timezone) - datetime.timedelta(hours=1)):
        # If just downloaded or checked, don't bother checking with the server
        print("Just downloaded: %s on %s" % (filename, lastdownload))
        return False

    try:
        with urllib.request.urlopen(url) as response:
            meta = response.headers
            try:
                lastmodified = dateCache.parse(meta['Last-Modified'])
                # print(F"last modified on server for {filename} is {lastmodified}")
            except:
                print(F"Server has no Last-Modified for {url}")
                lastmodified = datetime.datetime.now(
                    tz=timezone) - datetime.timedelta(hours=1)

            # print('last download: '+str(lastdownload))
            # print('last modified: '+str(lastmodified))

            if force or (lastmodified > lastdownload) or (os.path.getsize(filename) < 10):
                total_size = int(response.getheader('Content-Length').strip() or 0)
                print(f"Downloading new: {filename}, size {total_size}.")
                tempfile = "%s.tmp" % filename

                block_size = 1024  # 1 Kilobyte
                # Initialize tqdm only if running in a terminal
                if sys.stdout.isatty():
                    progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=tempfile)
                else:
                    progress_bar = None

                with open(tempfile, 'wb') as out_file:
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        out_file.write(buffer)
                        if progress_bar:
                            progress_bar.update(len(buffer))
                    if progress_bar:
                            progress_bar.close()

                if os.path.getsize(tempfile) > 100:
                    # Move the downloaded file in place
                    if os.path.isfile(filename):
                        os.remove(filename)
                    os.replace(tempfile, filename)
                else:
                    logError("No data received from `%s`." % url)
                    return False

                return True
            else:
                print("    Still fresh: %s last modified on server at %s" %
                      (filename, lastmodified))
                now = time.time()
                os.utime(filename, (now, now))
                return False
    except HTTPError as e:
        logError("Problem opening '%s': http error %d, %s" % (
            url, e.code, e.reason))
        return False
    except URLError as e:
        logError("Problem opening '%s': %s" % (url, e.reason))
        return False
    except FileNotFoundError as e:
        logError("Problem opening file. %s" % (e))
        return False


def readjson(filename):
    print('Reading '+filename)
    with open(filename, 'r') as json_file:
        return json.load(json_file)


def writejson(filename, adict):
    print('Writing '+filename)
    with open(filename, 'w') as file:
        file.write(json.dumps(adict))

def decimalstring(number):
    """Turns US 10,000.00 into EU 10.000,00"""

    if number == round(number) and len(str(number)) <= 4:
        return str(number)
    else:
        return "{:,}".format(number).replace(',', 'x').replace('.', ',').replace('x', '.')


def switchdecimals(numberstring):
    """Switches ',' with '.' and the other way around"""
    return numberstring.replace(',', 'x').replace('.', ',').replace('x', '.')


def isnewer(file1, file2):
    """Returns True if both files exist and file 1 is created later (is newer) than file 2 """
    return os.path.isfile(file1) and os.path.isfile(file2) and os.stat(file1).st_mtime > os.stat(file2).st_mtime


def logError(errorString):
    print(errorString)
    with open(os.path.join(cachedir,'errors.log'), 'a') as file:
        file.write(errorString+"\n")


def sortDictOnKey(dictionary):
    return dict(sorted(dictionary.items(), key=itemgetter(0)))

