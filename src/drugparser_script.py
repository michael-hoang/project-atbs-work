import os
import pandas as pd
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options


class DrugParser:
    """
    A class for parsing drug information from AmerisourceBergen's ABC ordering platform.
    """

    def __init__(
            self,
            username,
            password,
            driver_path,
            website_url,
            in_file,
            out_file,
            mode='default'
    ):
        self.service = Service(driver_path)
        self.options = Options()
        if mode == 'headless':
            self.options.add_argument('--headless')
        elif mode == 'default':
            self.options.add_experimental_option('detach', True)

        self.driver = webdriver.Edge(
            service=self.service, options=self.options
        )

        self.load_drug_spreadsheet(in_file)
        self.open_website(website_url)
        time.sleep(3)
        self.sign_in(username, password)
        time.sleep(3)
        self.go_to_abc_order()
        time.sleep(3)
        self.parse_dropship_data()
        self.export_dropship_data(out_file)

    def load_drug_spreadsheet(self, in_file):
        data = pd.read_excel(in_file)
        self.drug_df = pd.DataFrame(data, columns=['NDC', 'Item'])
        self.unique_drugs = {
            'NDC': [],
            'Item': [],
            'Drop Ship': []
        }

    def parse_dropship_data(self):
        for ndc, item in zip(self.drug_df['NDC'], self.drug_df['Item']):
            formatted_ndc = str(ndc).zfill(11)
            if formatted_ndc not in self.unique_drugs['NDC']:
                self.unique_drugs['NDC'].append(formatted_ndc)
                self.unique_drugs['Item'].append(item)
                self.search_ndc(formatted_ndc)
                time.sleep(3)
                isDropShip = str(self.check_if_dropship())
                self.unique_drugs['Drop Ship'].append(isDropShip)

    def export_dropship_data(self, out_file):
        df = pd.DataFrame(self.unique_drugs)
        writer = pd.ExcelWriter(
            out_file, engine='xlsxwriter')
        df.to_excel(
            writer, sheet_name='Drugs', startrow=0, startcol=0, index=False
        )
        writer.save()

    def open_website(self, website_url):
        self.driver.get(website_url)

    def sign_in(self, username: str, password: str):
        username_input = self.driver.find_element(By.ID, 'logonuidfield')
        username_input.send_keys(username)
        password_input = self.driver.find_element(By.ID, 'logonpassfield')
        password_input.send_keys(password)
        sign_in_btn = self.driver.find_element(By.NAME, 'uidPasswordLogon')
        sign_in_btn.click()

    def go_to_abc_order(self):
        abc_order = self.driver.find_element(By.LINK_TEXT, 'ABC ORDER')
        abc_order.click()

    def search_ndc(self, ndc):
        search_box = self.driver.find_element(By.CLASS_NAME, 'text-input')
        search_box.clear()
        search_box.send_keys(ndc)
        search_btn = self.driver.find_element(
            By.XPATH, '//*[@id="styled-nav-container"]/div[2]/div/div/div[2]/button'
        )
        search_btn.click()

    def check_if_dropship(self) -> bool:
        try:
            dropship = self.driver.find_element(
                By.XPATH, '//*[contains(text(), "Ships separately")]')
            if dropship.text:
                return True
        except:
            return False


if __name__ == '__main__':
    # Load environment variables from .env file
    load_dotenv()

    # Get environment variables
    USER = os.environ.get('USER')
    PASSWORD = os.environ.get('PASSWORD')

    # Paths
    WEBDRIVER_PATH = r'C:\Users\Mike\OneDrive\Desktop\edgedriver_win64\msedgedriver.exe'
    WEBSITE_URL = 'https://abcorderhs.amerisourcebergen.com/'
    IN_FILE = './assets/data/drugs.xlsx'
    OUT_FILE = './assets/data/output.xlsx'

    DrugParser(
        username=USER,
        password=PASSWORD,
        driver_path=WEBDRIVER_PATH,
        website_url=WEBSITE_URL,
        in_file=IN_FILE,
        out_file=OUT_FILE,
        mode='headless'
    )
