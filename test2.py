from requests import get
from json import dumps


ENDPOINT = "https://api.coronavirus.data.gov.uk/v1/data"
AREA_TYPE = "overview"  # "nation"
AREA_NAME = "england"

filters = [
    f"areaType={ AREA_TYPE }"  # , f"areaName={ AREA_NAME }"
]

structure = {
    "date": "date",
    "name": "areaName",
    "code": "areaCode",
    "dailyCases": "newCasesByPublishDate",
    "newAdmissions": "newAdmissions",
    "MVCases": "covidOccupiedMVBeds",
}


api_params = {
    "filters": str.join(";", filters),
    "structure": dumps(structure, separators=(",", ":")),
    "format": "csv"
}


formats = [
    "csv"  # , "json", "xml"
]


for fmt in formats:
    # api_params["format"] = fmt
    response = get(ENDPOINT, params=api_params, timeout=10)
    assert response.status_code == 200, f"Failed request for {fmt}: {response.text}"
    print(f"{fmt} data:")
    print(response.content.decode())
