from uk_covid19 import Cov19API
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import pandas
from ast import literal_eval

# from numpy.polynomial import polynomial

MAFREQ = 14  # frequency for moving average


def moving_average(a, n=3):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def exponential_fit(x, a, b):
    # return np.exp(a + b * x)
    return a * x + b


def getData(typ, areatype, areaname, splitdata=False):
    if splitdata is False:
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
            "Tests": "newTestsByPublishDate",
            "PCRTests": "newPCRTestsByPublishDate",
            "DeathCert": "newDailyNsoDeathsByDeathDate",
        }
        structure2 = None
    else:
        structure = {
            "date": "date",
            "name": "areaName",
            "code": "areaCode",
            "dailyCases": "newCasesByPublishDate",
            "newAdmissions": "newAdmissions",
            "Deaths": "newDeaths28DaysByPublishDate",
            "MVCases": "covidOccupiedMVBeds",
            "DoseA": "cumPeopleVaccinatedFirstDoseByPublishDate",
        }
        structure2 = {
            "date": "date",
            "name": "areaName",
            "code": "areaCode",
            "DoseB": "cumPeopleVaccinatedSecondDoseByPublishDate",
            "Tests": "newTestsByPublishDate",
            "PCRTests": "newPCRTestsByPublishDate",
            "DeathCert": "newDailyNsoDeathsByDeathDate",
        }
    if areatype == 'overview':
        filters = [f"areaType={ areatype }"]
    else:
        filters = [f"areaType={ areatype }", f"areaName={ areaname }"]
    api = Cov19API(filters=filters, structure=structure)
    upddt = api.get_release_timestamp()
    print('Data last updated: ', upddt)
    fname = os.path.join('./', areaname + '.csv')
    _ = api.get_csv(save_as=fname)
    data = pandas.read_csv(fname)
    if structure2 is not None:
        api = Cov19API(filters=filters, structure=structure2)
        upddt = api.get_release_timestamp()
        print('Data last updated: ', upddt)
        fname = os.path.join('./', areaname + '_2.csv')
        _ = api.get_csv(save_as=fname)
    data2 = pandas.read_csv(fname)
    data = data.set_index('date')
    data2 = data2.set_index('date')
    data2 = data2.drop(columns=['name','code'])
    data3 = pandas.concat([data,data2],axis=1)
    return data3


def getDemographicData(areatype, areaname):
    structure = {
        "date": "date",
        "name": "areaName",
        "code": "areaCode",
        "CasesByAge": "newCasesBySpecimenDateAgeDemographics"
    }
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
    fname = os.path.join('./', 'demographics-{}'.format(areaname) + '.csv')
    print(fname)
    _ = api.get_csv(save_as=fname)
    data = pandas.read_csv(fname,converters={"CasesByAge": literal_eval})
    tod = data[data['date']==max(data['date'])]
    vals = tod['CasesByAge'][0]
    with open('./case-demo-latest.csv', 'w') as outf:
        for val in vals:
            outf.write('{},{}\n'.format(val['age'], val['cases']))

    with open('./case-demo-all.csv', 'w') as outf:
        outf.write('areaCode,areaName,areaType,date,age,cases,rollingsum,rollingrate\n')
        for d in data.iterrows():
            vals = d[1]
            recdt=vals['date']
            name=vals['name']
            code=vals['code']
            for v in vals['CasesByAge']:
                outf.write('{},{},{},{},{},{},{},{}\n'.format(code, name,'nation',
                    recdt,v['age'], v['cases'], v['rollingSum'], v['rollingRate']))

    structure = {
        "date": "date",
        "name": "areaName",
        "code": "areaCode",
        "CasesByAge": "newDeaths28DaysByDeathDateAgeDemographics"
    }
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
    fname = os.path.join('./', 'deathdemographics-{}'.format(areaname) + '.csv')
    print(fname)
    _ = api.get_csv(save_as=fname)
    data = pandas.read_csv(fname,converters={"CasesByAge": literal_eval})
    tod = data[data['date']==max(data['date'])]
    vals = tod['CasesByAge'][0]
    with open('./death-demo-latest.csv', 'w') as outf:
        for val in vals:
            outf.write('{},{}\n'.format(val['age'], val['deaths']))

    with open('./death-demo-all.csv', 'w') as outf:
        outf.write('areaCode,areaName,areaType,date,age,deaths,rollingsum,rollingrate\n')
        for d in data.iterrows():
            vals = d[1]
            recdt=vals['date']
            name=vals['name']
            code=vals['code']
            for v in vals['CasesByAge']:
                outf.write('{},{},{},{},{},{},{},{}\n'.format(code, name,'nation',
                    recdt,v['age'], v['deaths'], v['rollingSum'], v['rollingRate']))


    structure = {
        "date": "date",
        "name": "areaName",
        "code": "areaCode",
        "VaccByAge": "vaccinationsAgeDemographics"
    }
    if areatype == 'overview':
        filters = [f"areaType={ areatype }"]

    else:
        filters = [f"areaType={ areatype }", f"areaName={ areaname }"]

    api = Cov19API(filters=filters, structure=structure)

    upddt = api.get_release_timestamp()
    print('Data last updated: ', upddt)

    # get data as csv. Can also get as json or xml
    # and save it to a file
    fname = os.path.join('./', 'vacc-demographics-{}'.format(areaname) + '.csv')
    print(fname)
    _ = api.get_csv(save_as=fname)
    data = pandas.read_csv(fname, converters={"VaccByAge": literal_eval})
    tod = data[data['date']==max(data['date'])]
    vals = tod['VaccByAge'][0]
    adultpop=0
    with open('./vacc-demo-latest.csv', 'w') as outf:
        for val in vals:
            outf.write('{},{}, {}\n'.format(val['age'], val['VaccineRegisterPopulationByVaccinationDate'], val['cumPeopleVaccinatedCompleteByVaccinationDate']))
            adultpop = adultpop + val['VaccineRegisterPopulationByVaccinationDate']

    return adultpop


def plotGraphs(data, adultpop):
    dts = pandas.to_datetime(data['date'],format='%Y-%m-%d')
    #cases = data['dailyCases']
    #admts = data['newAdmissions']
    #dths = data['Deaths']
    #cap = data['MVCases']
    dosea = data['DoseA']
    doseb = data['DoseB']

    dlyDoseA = -np.diff(dosea)
    dlyDoseB = -np.diff(doseb)
    totdlyDose = dlyDoseA + dlyDoseB
    plt.clf()
    fig, ax = plt.subplots()
    ax.plot(dts[1:], dlyDoseA, color='red', label = 'Dose 1')
    ax.plot(dts[1:], dlyDoseB, color='blue', label = 'Dose 2')
    ax.plot(dts[1:], totdlyDose, color='green', label = 'Total')
    ax.legend()
    #ax.ticklabel_format(style='plain')
    plt.title('Daily Vaccination Rate')
    plt.savefig('daily_vacc_rate.png')

    pctfullvacc = doseb  # *100.0/ adultpop
    adpopline = [adultpop] * len(pctfullvacc)
    for i in range(len(doseb)):
        if np.isnan(doseb[i]):
            adpopline[i] = np.nan
    
    fullvax = doseb.dropna().max()
    partvax = dosea.dropna().max()
    unvacad = (adultpop - partvax)/1e6
    prvacad = (adultpop - fullvax - unvacad)/1e6
    totpop = 66647112
    chldren = (totpop - adultpop)/1e6

    plt.clf()
    fig, ax = plt.subplots()
    plt.ticklabel_format(style='plain')
    ax.plot(dts, pctfullvacc, color='blue', label='Full')
    #ax.plot(dts, pctpartvacc, color='red', label='Part')
    ax.plot(dts, adpopline, color='red', label='Adult Population')
    
    ax.legend()
    plt.grid()
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    textstr = 'Unvaccinated: {:.1f}M adults and {:.1f}M children\nPart Vaccinated: {:.1f}M adults'.format(unvacad, chldren, prvacad)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=11,
        verticalalignment='top', bbox=props)
    plt.title('Percent of Adults Vaccinated')
    plt.savefig('vacc_pctage.png')


if __name__ == '__main__':

    # AREA_TYPE = 'ltla'                   'utla'    "region" "overview"
    # AREA_NAME = 'west oxfordshire'  'oxfordshire' 'england' ''

    if len(sys.argv) == 1:
        arg1 = 2
    else:
        arg1 = int(sys.argv[1])

    #alldata = getData(int(arg1), 'overview', 'overview')

    engl = getData(int(arg1), 'nation', 'England', splitdata=True) # england
    nire = getData(int(arg1), 'nation', 'Northern Ireland', splitdata=True) # NI
    scot = getData(int(arg1), 'nation', 'Scotland', splitdata=True) # scotland
    wale = getData(int(arg1), 'nation', 'Wales', splitdata=True) # wales
    engl = engl.drop(columns=['name','code'])
    scot = scot.drop(columns=['name','code'])
    wale = wale.drop(columns=['name','code'])
    nire = nire.drop(columns=['name','code'])
    alln = engl.add(scot, fill_value=0)
    alln = alln.add(wale, fill_value=0)
    alln = alln.add(nire, fill_value=0)
    alln['name']='United Kingdom'
    alln['code']='K02000001'
    alln=alln[['name','code','dailyCases','newAdmissions','Deaths','MVCases','DoseA','DoseB','Tests','PCRTests','DeathCert']]
    alln.to_csv('./overview.csv', index_label='date')
    
    getData(int(arg1), 'utla', 'oxfordshire')
    getData(int(arg1), 'ltla', 'west oxfordshire')

    adultpop = getDemographicData('Nation', 'England')

    #plotGraphs(alln, adultpop)
