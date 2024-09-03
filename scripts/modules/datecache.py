#!/usr/bin/env python3
# 
# Class caching parsed dates for speed optimization
import datetime
from dateutil import parser

class DateCache:
    """Class for caching parsed dates. Caching is way quicker than parsing."""
    cachedDates = {}
    cacheHits = 0
    cacheMisses = 0
    acceptDatesAfter = datetime.date.fromisoformat('2020-01-01')
    todaysDate = datetime.date.today()

    # Cache parsed dates.
    def parse(self, dateString):
        """Cache correctly parsed dates. Strings which are not
        valid dates are not cached, raise an exception and thus
        also slow things down."""
        try:
            fromcache = self.cachedDates[dateString]
            self.cacheHits += 1
            return fromcache
        except KeyError:
            self.cacheMisses += 1
            parseddate = parser.parse(dateString)
            self.cachedDates[dateString] = parseddate
            return parseddate

    def isvaliddate(self, datestring, filename=None):
        try:
            parseddate = self.parse(datestring)
            if (isinstance(parseddate, datetime.datetime)):
                parseddate = parseddate.date()
            else:
                raise ValueError(f"Invalid date {datestring}")

            if parseddate < self.acceptDatesAfter:
                raise ValueError(f"Date {datestring} is too old")

            if parseddate > self.todaysDate:
                raise ValueError(f"Date {datestring} is too new")
            
            return True
        except Exception as ex:
            if filename:
                print('Ignoring invalid date '+datestring+' in '+filename+'.')
            return False


    def today(self):
        return self.todaysDate


    def cacheUse(self):
        if (self.cacheMisses == 0):
            return 0
        else:
            return 100 * (self.cacheHits/(self.cacheHits + self.cacheMisses))


    def cacheReport(self):
        print("    earliest date: %s" % min(self.cachedDates.values()))
        print("      latest date: %s" % max(self.cachedDates.values()))
        print("  date cache size: %d" % len(self.cachedDates))
        print("  date cache hits: %d" % self.cacheHits)
        print("date cache misses: %d" % self.cacheMisses)
        print("        hit ratio: %d%%" % self.cacheUse())


dateCache = DateCache()

if __name__ == "__main__":
    for i in range(100):
        dateCache.isvaliddate('2024-02-01','a')
    for i in range(100):
        dateCache.isvaliddate('not a valid date')
    dateCache.cacheReport()