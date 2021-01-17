#
# get the ECDC's weekly data file
#

import csv
import urllib.request
import numpy as np
import datetime as dt


ecdctype = np.dtype([('dateRep', 'S10'), ('year_week', 'S8'),
    ('cases_weekly', 'i8'), ('deaths_weekly', 'i8'), ('Ctry', 'S40'),
    ('geoID', 'S4'), ('countryterritoryCode', 'S8'), ('popData2019', 'i8'), ('continentExp', 'S32'),
    ('notifrateper100k', 'f8')])


def getECDCdata():
    url = 'https://opendata.ecdc.europa.eu/covid19/casedistribution/csv'
    response = urllib.request.urlopen(url)
    lines = [li.decode('utf-8') for li in response.readlines()]
    cr = csv.reader(lines)
    with open('global-data.csv', 'w', newline='') as csvfile:
        fwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for rw in cr:
            if rw[0] != 'dateRep':
                dat = dt.datetime.strptime(rw[0], '%d/%m/%Y')
                rw[0] = dat
            rw[4] = rw[4].replace(', ', '_').replace(' ', '_')
            if rw[7] == '':
                rw[7] = '0'
            if rw[9] == '':
                rw[9] = '0'
            fwriter.writerow(rw)
            # print(rw)

    ecdcdata = np.loadtxt('global-data.csv', delimiter=',', skiprows=1, dtype=ecdctype)

    cond = (ecdcdata['Ctry'] == b'United_Kingdom')
    matchset = ecdcdata[cond]
    print(matchset)


if __name__ == '__main__':
    getECDCdata()
