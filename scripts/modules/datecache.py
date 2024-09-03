# Class caching parsed dates for speed optimization

class DateCache:
    cachedDates = {}
    cacheHits = 0
    cacheMisses = 0
    acceptDatesAfter = datetime.date.fromisoformat('2020-01-01')
    todaysDate = datetime.date.today()

    # class default constructor, if needed
    # def __init__(self):
    #     self.cachedDates = {}

    # Cache parsed dates.
    def parse(self, dateString):
        try:
            fromcache = self.cachedDates[dateString]
            self.cacheHits += 1
            return fromcache
        except KeyError:
            self.cacheMisses += 1
            parseddate = parser.parse(dateString)
            self.cachedDates[dateString] = parseddate
            return parseddate

    def isvaliddate(self, datestring, filename):
        parseddate = self.parse(datestring)

        if (isinstance(parseddate, datetime.datetime)):
            parseddate = parseddate.date()

        if parseddate >= self.acceptDatesAfter and parseddate <= self.todaysDate:
            return True
        elif filename:
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
        print("  date cache hits: %d" % self.cacheHits)
        print("date cache misses: %d" % self.cacheMisses)
        print("        hit ratio: %d%%" % self.cacheUse())


dateCache = DateCache()