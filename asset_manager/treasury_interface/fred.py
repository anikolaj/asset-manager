import json
import os
import requests
from datetime import date

from asset_manager.treasury_interface import TreasuryService


class Fred(TreasuryService):
    # API ENDPOINTS
    __FRED_TREASURY_RATE = "https://api.stlouisfed.org/fred/series/observations?series_id={}&file_type=json&limit=1&sort_order=desc&api_key={}"  # noqa

    # TREASURY SYMBOLS
    DGS30 = "DGS30"
    DGS10 = "DGS10"
    DGS5 = "DGS5"
    DGS1 = "DGS1"
    DGS6MO = "DGS6MO"
    DGS3MO = "DGS3MO"
    DGS1MO = "DGS1MO"

    def __init__(self, config: dict) -> None:
        self.__key = config["fred"]["key"]

        self.__UST30Y = self.__get_treasury_rate(self.DGS30)
        self.__UST10Y = self.__get_treasury_rate(self.DGS10)
        self.__UST5Y = self.__get_treasury_rate(self.DGS5)
        self.__UST1Y = self.__get_treasury_rate(self.DGS1)
        self.__UST6MO = self.__get_treasury_rate(self.DGS6MO)
        self.__UST3MO = self.__get_treasury_rate(self.DGS3MO)
        self.__UST1MO = self.__get_treasury_rate(self.DGS1MO)

    @property
    def UST30Y(self) -> float:
        return self.__UST30Y

    @property
    def UST10Y(self) -> float:
        return self.__UST10Y

    @property
    def UST5Y(self) -> float:
        return self.__UST5Y

    @property
    def UST1Y(self) -> float:
        return self.__UST1Y

    @property
    def UST6MO(self) -> float:
        return self.__UST6MO

    @property
    def UST3MO(self) -> float:
        return self.__UST3MO

    @property
    def UST1MO(self) -> float:
        return self.__UST1MO

    def __get_treasury_rate(self, symbol: str) -> float:
        today = date.today()

        current_directory = os.getcwd()
        symbol_directory = current_directory + "/asset_manager/data/treasury/{}/"
        symbol_directory = symbol_directory.format(symbol)

        if os.path.exists(symbol_directory) is False:
            os.makedirs(symbol_directory)
        os.chdir(symbol_directory)

        filename = str(today) + ".json"
        response = {}

        if os.path.exists(filename) is False:
            api_string = self.__FRED_TREASURY_RATE.format(symbol, self.__key)
            response = requests.get(api_string).json()

            # save response to file in directory
            with open(filename, "w") as json_file:
                json.dump(response, json_file)
        else:
            with open(filename, "r") as json_file:
                response = json.load(json_file)

        os.chdir(current_directory)

        rate = response["observations"][0]["value"]
        return float(rate)
