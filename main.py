
import requests
from xml.etree import ElementTree as ET
import time
import matplotlib.pyplot as plt


class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class CurrencyFetcher(metaclass=SingletonMeta):
    def __init__(self):
        self.last_request_time = 0
        self.currencies = []
        self.request_interval = 1

    def get_currencies(self, currencies_ids_lst):
        current_time = time.time()
        if current_time - self.last_request_time < self.request_interval:
            raise Exception(f"Запросы можно делать не чаще, чем раз в {self.request_interval} секунд.")

        self.last_request_time = current_time

        response = requests.get('http://www.cbr.ru/scripts/XML_daily.asp')
        root = ET.fromstring(response.content)
        self.currencies = []

        for valute in root.findall('Valute'):
            valute_id = valute.get('ID')
            if valute_id in currencies_ids_lst:
                name = valute.find('Name').text
                value = valute.find('Value').text.replace(',', '.')
                charcode = valute.find('CharCode').text
                nominal = int(valute.find('Nominal').text)
                value_per_unit = float(value) / nominal
                self.currencies.append({charcode: (name, f"{value_per_unit:.4f}")})

        return [currency for currency in self.currencies if
                currency[list(currency.keys())[0]] is not None]

    def visualize_currencies(self):
        fig, ax = plt.subplots()
        charcodes = [list(item.keys())[0] for item in self.currencies if item[list(item.keys())[0]] is not None]
        values = [float(list(item.values())[0][1]) for item in self.currencies if
                  item[list(item.keys())[0]] is not None]

        ax.bar(charcodes, values, color='green')
        ax.set_xlabel('Валюта')
        ax.set_ylabel('Курс (в рублях)')
        ax.set_title('Курсы валют')
        plt.savefig('currencies.jpg')
        plt.close()

if __name__ == "__main__":
    try:
        result = CurrencyFetcher().get_currencies(
            ['R01035',
             'R01335',
             'R01700J'])
        print(result)
        CurrencyFetcher().visualize_currencies()
    except Exception as e:
        print(e)
