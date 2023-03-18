import datetime
import math
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from decorator import LogDecorator


class Helen(object):
    @LogDecorator()
    def __init_geckodriver(self, verbose):
        options = Options()
        if verbose == 0:
            options.add_argument("-headless")
        options.add_argument("-profile")
        options.add_argument(".selenium")
        # options.set_preference("browser.download.folderList", 2)
        # options.set_preference("browser.download.dir", './dl')

        return webdriver.Firefox(
            options=options, service_args=["--marionette-port", "2828"]
        )

    @LogDecorator()
    def __init__(self, database, username, password, delivery_site_id, start_date, verbose):

        self.database = database
        self.username = username
        self.password = password
        self.verbose = verbose
        self.delivery_site_id = delivery_site_id

        if start_date is None:
            t = datetime.now()
            self.start_date = datetime(year=t.year,month=t.month,day=t.day, hour=0, minute=0, second=0, tzinfo=timezone.utc) + timedelta(days=-7)
        else:
            t = datetime.strptime(start_date[0], "%Y-%m-%d")
            self.start_date = datetime(year=t.year,month=t.month,day=t.day, hour=0, minute=0, second=0, tzinfo=timezone.utc)
        t = datetime.now()
        self.end_date = datetime(year=t.year,month=t.month,day=t.day, hour=0, minute=0, second=0, tzinfo=timezone.utc)

        if delivery_site_id != None:
            self.__fetch_with_helen_electricity_usage()
        else:
            self.__fetch_with_selenium()

    @LogDecorator()
    def __fetch_with_helen_electricity_usage(self):
        import helen_electricity_usage  # refactored version, setup.py install --user this branch https://github.com/Janska85/python-helen-electricity-usage/tree/develop/refactor-to-new-portal

        helen = helen_electricity_usage.Helen(self.username, self.password, self.delivery_site_id)
        helen.login()
        data = helen.get_electricity(self.start_date, self.end_date)
        
        
        data = data['intervals']['electricity'][0]
        idx = pandas.date_range(start=datetime.strptime( data['start'], "%Y-%m-%dT%H:%M:%S+00:00"), end=(datetime.strptime( data['stop'], "%Y-%m-%dT%H:%M:%S+00:00") + timedelta(hours=-1)), freq='H')
        pa = pandas.array(data['measurements'])

        df = pandas.DataFrame(data=pa, index=idx)
        for row in df.itertuples():
            data_tuple = (row[0].tz_localize('utc').tz_convert('Europe/Helsinki'), row[1]['value'])
            self.database.insert_or_update("kwh", data_tuple)

    @LogDecorator()
    def __fetch_with_selenium(self):
        self.driver = self.__init_geckodriver(self.verbose)

        try:
            self.__login(self.username, self.password)
            self.__get_consumption()
            if self.fpath != None:
                pd_excel_df = pandas.read_excel(Path(self.fpath))
                for row in pd_excel_df.itertuples():
                    kw = row[2]
                    if math.isnan(kw):
                        kw = 0.0
                    data_tuple = (row[1].tz_localize('Europe/Helsinki'), kw)
                    self.database.insert_or_update("kwh", data_tuple)
                os.remove(self.fpath)
        except Exception as ex:
            self.driver.close()
            raise ex
        self.driver.close()

    @LogDecorator()
    def __login(self, username, password):
        self.driver.get("https://www.helen.fi/kirjautuminen")
        self.driver.switch_to.frame(0)
        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.XPATH,"/html/body/table/tbody/tr/td/div/div[2]/div[2]/div/div[3]/div/form/div/span/input").click()
        time.sleep(10)  # for now wait here statically the redirections to finish
        self.driver.switch_to.default_content()
        try: 
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, "recharts-wrapper"))
            )
        except Exception as ex:
            raise ex

    @LogDecorator()
    def __get_consumption(self):
        self.driver.get(
            "https://web.omahelen.fi/personal/reports/electricity-consumption"
        )
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "recharts-surface"))
        )

        for elem in self.driver.find_elements(By.XPATH, "//button"):
            if elem.get_attribute("data-cy") == "downloadExcel":
                elem.click()

        self.driver.find_element(By.XPATH, '//*[@id="downshift-0-toggle-button"]').click()
        self.driver.find_element(By.XPATH, '//*[@id="downshift-0-item-3"]').click()
        self.driver.find_element(By.XPATH, '//*[@id="date1"]').send_keys(Keys.CONTROL, "a", Keys.DELETE)
        self.driver.find_element(By.XPATH, '//*[@id="date1"]').send_keys(self.start_date.strftime("%d.%m.%Y"))
        self.driver.find_element(By.XPATH, '//*[@id="date2"]').send_keys(Keys.CONTROL, "a", Keys.DELETE)
        self.driver.find_element(By.XPATH, '//*[@id="date2"]').send_keys(self.end_date.strftime("%d.%m.%Y"))
        self.driver.find_element(By.XPATH, '//*[@id="downshift-1-toggle-button"]').click()
        self.driver.find_element(By.XPATH, '//*[@id="downshift-1-item-0"]').click()
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[3]/div/button[2]").click()
        self.fpath = f"./dl/electricity_report_{ self.start_date.strftime('%d_%m_%Y') }_{ self.end_date.strftime('%d_%m_%Y') }.xlsx"

        # wait for the file to be downloaded
        for i in range(1, 15):
            time.sleep(5)
            if os.path.exists(self.fpath):
                file_exists = True
                break

        if not file_exists:
            raise ValueError('Download probably failed.')