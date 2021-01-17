from uk_covid19 import Cov19API
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import csv
import sys
import os
from datetime import datetime as dt
# from numpy.polynomial import polynomial

MAFREQ = 14  # frequency for moving average


structure = {
    "date": "date",
    "name": "areaName",
    "code": "areaCode",
    "dailyCases": "newCasesByPublishDate",
    "newAdmissions": "newAdmissions",
    "Deaths": "newDeaths28DaysByPublishDate",
    "MVCases": "covidOccupiedMVBeds",
    "DoseA": "cumPeopleVaccinatedFirstDoseByPublishDate",
    "DoseB": "cumPeopleVaccinatedSecondDoseByPublishDate",
}


def moving_average(a, n=3):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def exponential_fit(x, a, b):
    # return np.exp(a + b * x)
    return a * x + b


def getData(typ, areatype, areaname):
    if areatype == 'overview':
        filters = [f"areaType={ areatype }"]

    else:
        filters = [f"areaType={ areatype }", f"areaName={ areaname }"]

    api = Cov19API(filters=filters, structure=structure)

    upddt = api.get_release_timestamp()
    print('Data last updated: ', upddt)

    # get data as csv. Can also get as json or xml
    # and save it to a file
    # data = api.get_csv()
    fname = os.path.join('./', areaname + '.csv')
    _ = api.get_csv(save_as=fname)

    return fname


def plotGraphs(fname, typ, areatype, areaname):
    dts = []
    cases = []
    admts = []
    dths = []
    cma = []
    cap = []
    tstamps = []

    with open(fname) as csvfile:
        plots = csv.reader(csvfile, delimiter=',')
        _ = next(plots)   # skip header row
        for row in plots:
            if len(row) > 0:
                # print(row)
                dat = dt.strptime(row[0], '%Y-%m-%d')
                dts.append(dat)
                tstamps.append(dat.timestamp())
                cases.append(int(row[3]))
                if len(row[4]) > 0:
                    admts.append(int(row[4]))
                else:
                    admts.append(0)
                if len(row[5]) > 0:
                    dths.append(int(row[5]))
                else:
                    dths.append(0)
                if len(row[6]) > 0:
                    cap.append(int(row[6]))
                else:
                    cap.append(0)

    for i in range(len(cases)):
        if cases[i] == 0:
            break
    cases = cases[:i]
    dths = dths[:i]
    dts = dts[:i]
    admts = admts[:i]
    cap = cap[:i]
    tstamps = tstamps[:i]

    latestdths = 0
    for d in dths:
        if d > 0:
            latestdths = d
            break

    print('latest data ', dts[0], cases[0], latestdths)

    cma = moving_average(cases, MAFREQ)
    for i in range(MAFREQ - 1):
        cma = np.append(cma, [[0]])  # pad moving average with zeros

    lbl = 'Unknown'
    ldths = np.log(dths)
    dispname = areaname
    if areatype == 'overview':
        dispname = 'National'

    # miny = 5
    if typ == 1:
        lbl = "Deaths - " + dispname
        ldths = np.log(dths)
        # miny = min(ldths) - 0.2
    elif typ == 2:
        lbl = "New Cases - " + dispname
        ldths = np.log(cases)
        # miny = 1000
    elif typ == 3:
        lbl = "Req Ventilation - " + dispname
        ldths = np.log(cap)
        # miny = 40
    elif typ == 4:
        lbl = "Hosp Adm - " + dispname
        ldths = np.log(admts)
        # miny = 90

    nldths = []
    nts = []
    pdts = []

    for i in range(len(ldths)):
        if ldths[i] > float('-inf'):
            nldths.append(ldths[i])
            nts.append(float(tstamps[i]))
            pdts.append(dt.fromtimestamp(tstamps[i]))

    # extend the data using an exponential fit
    # coeffs = polynomial.polyfit(np.asarray(nts), np.asarray(nldths), 1)
    # dfit = polynomial.Polynomial(coeffs)

    next1 = nts[0]
    for i in range(6):
        n = next1 + (7 * i) * 86400
        nts = np.concatenate(([n], nts))
        pdts = np.concatenate(([dt.fromtimestamp(n)], pdts))
        nldths = np.concatenate(([0], nldths))

    # fitdths = dfit(np.asarray(nts))

    if False:
        fig, ax1 = plt.subplots()

        # ax1.plot(dts, cma, label='cases')
        ax1.plot(dts, cases, label='New Cases (left)', color='tab:blue')
        ax1.set_ylabel('Cases')

        ax2 = ax1.twinx()  # use same x-axis
        ax2.plot(dts, admts, label='Hosp Adm (right)', color='tab:green')
        ax2.plot(dts, dths, label='deaths (right)', color='tab:red')
        ax2.set_ylabel('Hosp Adm / Deaths')

        # ask matplotlib for the plotted objects and their labels
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc='upper center')

        # plt.plot(dts, cap, label='capacity')

        plt.xlabel('Date')
        # plt.ylabel('Number')
        plt.title('Number of COVID Cases, Admissions & Deaths')

        ax2.xaxis.set_major_formatter(mdates.DateFormatter("%y-%m"))
        ax2.xaxis.set_minor_formatter(mdates.DateFormatter("%y-%m"))
        _ = plt.xticks(rotation=90)

        # fig.tight_layout()
        # plt.show()

    fig, ax1 = plt.subplots()

    ax1.scatter(pdts, np.exp(nldths), label=lbl, color='tab:blue')
    ax1.set_ylabel('Number')
    ax1.set_yscale('log')
    # ax1.plot(pdts, np.exp(fitdths), label='Fit', color='tab:green')
    ax1.grid()
    ax1.legend(loc='upper center')
    # ax1.set_ylim(miny)
    fig.tight_layout()
    plt.show()


if __name__ == '__main__':

    # AREA_TYPE = 'ltla'                   'utla'    "region" "overview"
    # AREA_NAME = 'west oxfordshire'  'oxfordshire' 'england' ''

    if len(sys.argv) == 1:
        arg1 = 2
        plots = False
    else:
        arg1 = sys.argv[1]
        plots = True

    fname = getData(int(arg1), 'overview', 'overview')
    getData(int(arg1), 'utla', 'oxfordshire')
    getData(int(arg1), 'ltla', 'west oxfordshire')
    if plots is True:
        plotGraphs(fname, int(arg1), 'overview', 'overview')
