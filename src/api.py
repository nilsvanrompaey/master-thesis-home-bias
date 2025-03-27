import requests

url = 'http://dataservices.imf.org/REST/SDMX_JSON.svc/'
key = 'Dataflow'  # Method with series information
search_term = 'CPIS'  # Term to find in series names
series_list = requests.get(f'{url}{key}').json()\
            ['Structure']['Dataflows']['Dataflow']

# Use dict keys to navigate through results:
for series in series_list:
    if search_term in series['Name']['#text']:
        print(f"{series['Name']['#text']}: {series['KeyFamilyRef']['KeyFamilyID']}")

key = 'DataStructure/CPIS'  # Method / series
dimension_list = requests.get(f'{url}{key}').json()\
            ['Structure']['KeyFamilies']['KeyFamily']\
            ['Components']['Dimension']
for n, dimension in enumerate(dimension_list):
    print(f'Dimension {n+1}: {dimension['@codelist']}')

key = f"CodeList/{dimension_list[2]['@codelist']}"
code_list = requests.get(f'{url}{key}').json()\
	    ['Structure']['CodeLists']['CodeList']['Code']
for code in code_list:
    print(f"{code['Description']['#text']}: {code['@value']}")

country_str = ""
for country in ["BE", "US", "DE"]:
    country_str += f"{country}+"
country_str = country_str[:-1]
print(country_str)

key = f"CompactData/CPIS/A.{country_str}.I_A_E_T_T_BP6_USD.T.T.{country_str}"
# key = "CompactData/IFS/M.GB.PMP_IX"
data = (requests.get(f'{url}{key}').json())

data["CompactData"]["DataSet"]["Series"].__len__()