# Import dictionaries from separate files
from utils.constants_values.ds_country_to_code import DS_COUNTRY_TO_CODE
from utils.constants_values.wfe_country_to_code import WFE_COUNTRY_TO_CODE
from utils.constants_values.wfe_exchange_to_code import WFE_EXCHANGE_TO_CODE
from utils.constants_values.cpis_column_headers import CPIS_COLUMN_HEADERS, CPIS_COLUMN_HEADERS_HALF
from utils.constants_values.cpis_country_to_code import CPIS_COUNTRY_TO_CODE
from utils.constants_values.countries import MAJOR_ECONOMIES, OFFSHORE_CENTERS
from utils.constants_values.wfe_modifications import WFE_MODIFICATIONS
from utils.constants_values.wb_codes_2_to_3 import WB_CODES_2_TO_3
from utils.constants_values.ds_id_modifications import DS_ID_MODIFICATIONS

class DS:
    COUNTRY_TO_CODE = DS_COUNTRY_TO_CODE
    COUNTRIES = list(COUNTRY_TO_CODE.keys())
    CODES = list(COUNTRY_TO_CODE.values())
    CODE_TO_COUNTRY = {v: k for k, v in COUNTRY_TO_CODE.items()}
    ID_MODIFICATIONS = DS_ID_MODIFICATIONS

class WFE:
    COUNTRY_TO_CODE = WFE_COUNTRY_TO_CODE
    EXCHANGE_TO_CODE = WFE_EXCHANGE_TO_CODE
    CODE_TO_COUNTRY = {v: k for k, v in COUNTRY_TO_CODE.items()}
    COUNTRIES = list(COUNTRY_TO_CODE.keys())
    CODES = list(COUNTRY_TO_CODE.values())
    WFE_MODIFICATIONS = WFE_MODIFICATIONS

class CPIS:
    COLUMN_HEADERS = CPIS_COLUMN_HEADERS
    COLUMN_HEADERS_HALF = CPIS_COLUMN_HEADERS_HALF
    COUNTRY_TO_CODE = CPIS_COUNTRY_TO_CODE
    CODE_TO_COUNTRY = {v: k for k, v in COUNTRY_TO_CODE.items()}
    COUNTRIES = list(CPIS_COUNTRY_TO_CODE.keys())
    CODES = list(CPIS_COUNTRY_TO_CODE.values())

class WB:
    CODES_2_TO_3 = WB_CODES_2_TO_3
    CODES_3_TO_2 = {v: k for k, v in CODES_2_TO_3.items()}

class COUNTRIES:
    MAJOR = MAJOR_ECONOMIES
    OFFSHORE = OFFSHORE_CENTERS