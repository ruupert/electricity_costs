from datetime import datetime, timedelta

import pandas as pd
import requests
from entsoe import EntsoePandasClient


class Entsoee:

    def __init__(self, database, api_key, country, tz):
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
        start_date = datetime.now() + timedelta(days=-5)
        end_date = datetime.now() + timedelta(days=2)
        start = pd.Timestamp(start_date, tz=self.tz)
        end = pd.Timestamp(end_date, tz=self.tz)
        try:
            ts = client.query_day_ahead_prices(self.country,
                                               start=start,
                                               end=end)
            return ts
        except requests.HTTPError:
            return None