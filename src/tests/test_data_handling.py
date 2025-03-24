# Standard Library Imports (if any)

# Third-party Library Imports
import numpy as np

# Local Module Imports
from data_handling import *

class TestDataHandling():
    def __init__(self):
        data = DataManager(raw_dir = "./data/raw",
                        save_dir = "./data/clean")

        data.load_data()
        self.cpis = data.get_dataset("cpis")
        self.wfe = data.get_dataset("wfe")
        self.ds = data.get_dataset("ds")
        self.fed = data.get_dataset("fed")

    def test_all(self):
        self.test_data_handling_importing_saving_and_loading()
        self.test_data_handling_cpis_get_data()

    def test_data_handling_importing_saving_and_loading(self):

        data_raw = DataManager(raw_dir = "./data/raw",
                                save_dir = "./data/clean")

        data_raw.clean_and_save_data()
        assert data_raw.get_dataset("cpis").equals(self.cpis), "cpis issue"
        assert data_raw.get_dataset("wfe").equals(self.wfe), "wfe issue"
        assert data_raw.get_dataset("ds").equals(self.ds), "ds issue"
        assert data_raw.get_dataset("fed").equals(self.fed), "fed issue"

        print("test_data_handling_importing_saving_and_loading passed.")

    def test_data_handling_cpis_get_data(self):

        de_at_2005 = self.cpis.get_data(holders="Germany",
                issuers="Austria",
                periods=2005)
        assert np.isclose(de_at_2005, 5117538600.0), "de_at_2005"
        print("test_data_handling_cpis_get_data passed.")