#
# get covid data from gov website
#

conda activate covid19
$loc=get-location
set-location $psscriptroot
set-location C:\Users\Mark\OneDrive\Documents\Covid19\data
Write-Output $args
# world data got in getECDCdata.py
# wget https://covid.ourworldindata.org/data/owid-covid-data.csv
python $psscriptroot\getECDCdata.py 
python $psscriptroot\getCovidData.py $args[0]
set-location $loc