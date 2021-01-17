#
# get covid data from gov website
#

conda activate covid19
set-location $psscriptroot
Write-Output $args
python .\getECDCdata.py 
python getCovidData.py $args[0]