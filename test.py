# testing the covid19 python interface

from requests import get


def get_data(url):
    response = get(endpoint, timeout=10)

    if response.status_code >= 400:
        raise RuntimeError(f'Request failed: { response.text }')

    return response.json()


if __name__ == '__main__':
    endpoint = (
        'https://api.coronavirus.data.gov.uk/v1/data?'
        # 'filters=areaType=nation;areaName=england&'
        'filters=areaType=overview&'
        # 'structure={"date":"date","newCases":"newCasesByPublishDate"}'
        'structure={"date":"date","newAdmissions":"newAdmissions","MVCases":"covidOccupiedMVBeds"}&'
        'format="csv"'
    )

    data = get_data(endpoint)
    print(data)
