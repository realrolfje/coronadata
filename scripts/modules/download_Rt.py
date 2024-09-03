#!/usr/bin/env python3
# Downloads the Rt dataset.
# See data.rivm.nl, Covid-19 reproductiegetal
# See https://data.rivm.nl/meta/srv/dut/catalog.search#/metadata/ed0699d1-c9d5-4436-8517-27eb993eab6e
import os
from utilities import downloadIfStale
from defaults import datadir


def download_Rt():
    downloadIfStale(
        filename=os.path.join(datadir, "COVID-19_reproductiegetal.json"),
        url="https://data.rivm.nl/covid-19/COVID-19_reproductiegetal.json")


if __name__ == "__main__":
    download_Rt()
