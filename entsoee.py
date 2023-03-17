from datetime import datetime, timedelta

import pandas as pd
import requests
from entsoe import EntsoePandasClient


class Entsoee:

    def __init__(self, database, api_key, country, tz, start_date):

        if start_date is None:
            self.start_date = datetime.now() + timedelta(days=-7)
        else: 
            self.start_date = datetime.strptime(start_date, "%Y-%m-%d")

        self.end_date = datetime.now() + timedelta(days=2)

        self.api_key = api_key
        self.country = country
        self.tz = tz
        spot_data = self.__fetch_prices()
        if spot_data is not None:
            for key in spot_data.keys():
                data_tuple = (key.strftime("%Y-%m-%d %H:%M:%S"),
                              spot_data[key] / 10)
                database.insert_or_update("price", data_tuple)

    def __fetch_prices(self):
        client = EntsoePandasClient(api_key=self.api_key)
        start = pd.Timestamp(self.start_date, tz=self.tz)
        end = pd.Timestamp(self.end_date, tz=self.tz)
        try:
            ts = client.query_day_ahead_prices(self.country,
                                               start=start,
                                               end=end)
            return ts
        except requests.HTTPError:
            return None