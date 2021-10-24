#
# get the ECDC's weekly data file
#

import csv
import urllib.request
import numpy as np
import datetime as dt


ecdctype = np.dtype([('dateRep', 'S10'), 
    ('day', 'i4'), ('month', 'i4'), ('year', 'i4'),
    ('cases_weekly', 'i8'), ('deaths_weekly', 'i8'), 
    ('Ctry', 'S40'), ('geoID', 'S4'), ('countryterritoryCode', 'S8'), 
    ('popData2019', 'i8'), ('continentExp', 'S32'),
    ('notifrateper100k', 'S10')])


def getECDCdata():
    url = 'https://opendata.ecdc.europa.eu/covid19/nationalcasedeath_eueea_daily_ei/csv/data.csv'
    response = urllib.request.urlopen(url)
    lines = [li.decode('utf-8') for li in response.readlines()]
    cr = csv.reader(lines)
    with open('eu-data.csv', 'w', newline='') as csvfile:
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


def getWorldData():
    url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
    response = urllib.request.urlopen(url)
    lines = [li.decode('utf-8') for li in response.readlines()]
    with open('new-global-data.csv', 'w', newline='') as csvfile:
        for li in lines:
            csvfile.write('{}'.format(li))


if __name__ == '__main__':
    getECDCdata()
    getWorldData()
