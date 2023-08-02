import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import time
import os

from helen import Helen

class TestHelen(unittest.TestCase):

    @patch('helen.webdriver')
    def test___init__(self, webdriver_mock):
        # Arrange
        start_date = None
        tz = 'UTC'
        database_mock = MagicMock()
        username = "testuser"
        password = "testpass"
        delivery_site_id = None
        verbose = False
        helen = Helen(database_mock, username, password, delivery_site_id, tz, start_date, verbose)

        # Assert
        self.assertIsNotNone(helen.start_date)
        self.assertIsNotNone(helen.end_date)

    @patch('helen.webdriver')
    def test___fetch_with_selenium(self, webdriver_mock):
        # Arrange
        start_date = None
        tz = 'UTC'
        database_mock = MagicMock()
        username = "testuser"
        password = "testpass"
        delivery_site_id = None
        verbose = False
        helen = Helen(database_mock, username, password, delivery_site_id, tz, start_date, verbose)
        helen.__login = MagicMock()
        helen.__get_consumption = MagicMock()
        helen.fpath = "test_files/test_file.xlsx"
        
        Path("test_files").mkdir(parents=True, exist_ok=True)
        Path("test_files/test_file.xlsx").touch()

        # Act
        helen.__fetch_with_selenium()

        # Assert
        helen.__login.assert_called()
        helen.__get_consumption.assert_called()
        database_mock.insert_or_update.assert_called()

        #Clean-up
        os.remove(helen.fpath)
        path = Path("test_files")
        path.rmdir()

    def test___login(self):
        # Arrange
        start_date = None
        tz = 'UTC'
        database_mock = MagicMock()
        username = "testuser"
        password = "testpass"
        delivery_site_id = None
        verbose = False
        helen = Helen(database_mock, username, password, delivery_site_id, tz, start_date, verbose)

        # Mock the necessary calls 
        fake_wait_until_called = False

        fake_driver = MagicMock()
        fake_driver.find_element.return_value = MagicMock()
        fake_driver.switch_to.frame.return_value = MagicMock()
        fake_driver.switch_to.default_content.return_value = MagicMock()
        WebDriverWait = MagicMock()

        def presence_of_element_located(arg):
            nonlocal fake_wait_until_called
            fake_wait_until_called = True
            return True

        WebDriverWait.until.return_value = presence_of_element_located

        helen.driver = fake_driver

        # Act
        helen.__login(username, password)
        time.sleep(2)
        self.assertTrue(fake_wait_until_called)

    def test___get_consumption(self):
        # Arrange
        start_date = None
        tz = 'UTC'
        database_mock = MagicMock()
        username = "testuser"
        password = "testpass"
        delivery_site_id = None
        verbose = False
        helen = Helen(database_mock, username, password, delivery_site_id, tz, start_date, verbose)

        # Mock the necessary calls 
        fake_wait_until_called = False

        fake_driver = MagicMock()
        fake_driver.find_element.return_value = MagicMock()
        fake_driver.switch_to.frame.return_value = MagicMock()
        fake_driver.switch_to.default_content.return_value = MagicMock()
        WebDriverWait = MagicMock()

        def presence_of_element_located(arg):
            nonlocal fake_wait_until_called
            fake_wait_until_called = True
            return True

        def mock_element_click():
            pass

        fake_driver.find_elements.return_value = [
          MagicMock(get_attribute=lambda arg: "downloadExcel")
        ]

        fake_driver.execute_script.return_value = None
