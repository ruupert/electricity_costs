from datetime import datetime, timedelta, timezone

import pandas as pd
import requests
from entsoe import EntsoePandasClient

from decorator import LogDecorator


class Entsoee(object):

    @LogDecorator()
    def __init__(self, database, api_key, country, tz, start_date):

        if start_date is None:
            t = datetime.now()
            self.start_date = datetime(year=t.year,month=t.month,day=t.day, hour=0, minute=0, second=0, tzinfo=timezone.utc) + timedelta(days=-7)
        else: 
            t = datetime.strptime(start_date[0], "%Y-%m-%d")
            self.start_date = datetime(year=t.year,month=t.month,day=t.day, hour=0, minute=0, second=0, tzinfo=timezone.utc)
        t = datetime.now()
        self.end_date = datetime(year=t.year,month=t.month,day=t.day, hour=0, minute=0, second=0, tzinfo=timezone.utc) + timedelta(days=2)

        self.api_key = api_key
        self.country = country
        self.tz = tz
        spot_data = self.__fetch_prices()
        if spot_data is not None:
            for key in spot_data.keys():
                data_tuple = (key.tz_convert(self.tz),
                              spot_data[key] / 10)
                database.insert_or_update("price", data_tuple)

    @LogDecorator()
    def __fetch_prices(self):
        client = EntsoePandasClient(api_key=self.api_key)
        start = pd.Timestamp(self.start_date).tz_convert(self.tz)
        end = pd.Timestamp(self.end_date).tz_convert(self.tz)
        try:
            ts = client.query_day_ahead_prices(self.country,
                                               start=start,
                                               end=end)
            return ts
        except requests.HTTPError as ex:
            raise ex