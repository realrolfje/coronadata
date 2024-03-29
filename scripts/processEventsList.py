#!/usr/bin/env python3
#
import modules.brondata as brondata
from string import Template
from modules.datautil import runIfNewData
import sys

def main():
    runIfNewData(__file__)
    events = brondata.readjson('../data/measures-events.json')
    processEventsList(events)

def processEventsList(events):
    outputfilename = '../docs/events.html'
    with open(outputfilename, 'w') as outputfile:
        outputfile.write("""<html>
    <head>
        <title>Corona data landelijk</title>
        <meta name="viewport" content="width=device-width, user-scalable=yes, initial-scale=1">
        <link rel="stylesheet" href="styles.css">
        <link rel="apple-touch-icon" sizes="180x180" href="icons/apple-touch-icon.png">
    </head>
    <body>
        <p class="highlight header center">
            Geen smoesjes, je weet het best:<br />
            <b>Houd afstand, werk thuis, was je handen, vermijd drukke plaatsen.</b>
        </p>

        <div class="container center">
        <p>Alle persmomenten, nieuws en regels op een rijtje:</p>
        <table style="  margin-left: auto;  margin-right: auto;" width="400px">
        <tr><th align="left" width="100px">datum</th><th align="left" >gebeurtenis</th</tr>""")


        template = "<tr><td valign=\"top\">${date}</td><td valign=\"top\">${event}</td></tr>"
        link_template = "<tr><td valign=\"top\">${date}</td><td valign=\"top\"><a href=\"${url}\">${event}</a></td></tr>"

        for event in events:
            event['event'] = event['event'].replace('\n',' ')
            if 'url' in event:
                outputfile.write(Template(link_template).substitute(event))
            else:
                outputfile.write(Template(template).substitute(event))
        
        outputfile.write("""</table>
        </div>
    </body>
    </html>""")

if __name__ == '__main__':
    sys.exit(main())