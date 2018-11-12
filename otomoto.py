import requests
from bs4 import BeautifulSoup
import re
import math
import sys
import time
import tqdm

class Otomoto():
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'}
    prices = []
    mileages = []
    prod_years = {}
    fuel_types = {}
    engine_displacements = {}
    car_names = {}
    _engine_displacement_pattern = '(\d+ \d+) cm3'
    _price_pattern = '\d+ \d+'
    _mileage_pattern = '(\d+ \d+) km'
    _year_pattern = '\d{4}'
    _fuel_pattern = 'Benzyna|Benzyna\+LPG|Diesel|Benzyna\+CNG|Hybryda|Elektryczny|Wodór|Etanol'

    def __init__(self, base_url):
        self.base_url = base_url

    def _count_pages(self):
        r = requests.get(self.base_url, headers=self.headers).text
        soup = BeautifulSoup(r, "html.parser")
        pages = soup.find_all('span', 'page')
        return int(pages[-1].text.strip())

    def get_offers(self, ):
        for page in tqdm.tqdm(range(1, self._count_pages() + 1)):  # self._count_pages() + 1
            url = self.base_url + '&page={}'.format(page)
            r = requests.get(url, headers=self.headers).text
            soup = BeautifulSoup(r, "html.parser")
            offers = soup.find_all('div', 'offer-item__content')
            self._extract_data(offers)

    def _get_price(self, offer):
        netto_brutto = offer.find('span', 'offer-price__details').text
        price = offer.find('span', 'offer-price__number').text
        try:
            if re.search('Netto', netto_brutto):
                price = int(re.search(self._price_pattern, price).group().replace(' ','')) * 1.23
            else:
                price = int(re.search(self._price_pattern, price).group().replace(' ',''))
            self.prices.append(price)
        except Exception:
            pass

    def _get_mileage(self, offer):
        mileage = offer.find('ul', 'offer-item__params').text
        mileage = re.search(self._mileage_pattern, mileage)
        if mileage: self.mileages.append(int(mileage.group(1).replace(' ', '')))

    def _get_years(self, offer):
        year = offer.find('ul', 'offer-item__params').text
        year = re.search(self._year_pattern, year)
        if year:
            year = year.group()
            try:
                self.prod_years[int(year)] += 1
            except Exception:
                self.prod_years[int(year)] = 1

    def _get_fuel_types(self, offer):
        fuel = offer.find('ul', 'offer-item__params').text
        fuel = re.search(self._fuel_pattern, fuel)
        if fuel:
            fuel = fuel.group().strip()
            try:
                self.fuel_types[fuel] += 1
            except Exception:
                self.fuel_types[fuel] = 1

    def _get_engine_displacements(self, offer):
        engine_displacement = offer.find('ul', 'offer-item__params').text
        engine_displacement = re.search(self._engine_displacement_pattern, engine_displacement)
        if engine_displacement:
            engine_displacement = engine_displacement.group(1).replace(' ', '')
            try:
                self.engine_displacements[engine_displacement] += 1
            except Exception:
                self.engine_displacements[engine_displacement] = 1

    def _get_car_names(self, offer):
        car_name = offer.find('a', 'offer-title__link').text.strip()
        if car_name:
            try:
                self.car_names[car_name] += 1
            except Exception:
                self.car_names[car_name] = 1

    def _calculate_average_price(self):
        return round(sum(self.prices)/len(self.prices), 2)

    def _calculate_average_mileage(self):
        return round(sum(self.mileages)/len(self.mileages), 2)

    def _calculate_average_year(self):
        year_sum = 0 # sum of all production years
        count_years = 0 # number of production years to calculate average year
        for year, number in self.prod_years.items():
            year_sum += year * number
            count_years += number
        return math.floor(year_sum/count_years)

    @staticmethod
    def _get_most_popular_value(values):
        maximum = max(values, key=values.get)
        return {maximum: values[maximum]}

    def _extract_data(self, offers):
        for offer in offers:
            self._get_price(offer)
            self._get_mileage(offer)
            self._get_years(offer)
            self._get_fuel_types(offer)
            self._get_engine_displacements(offer)
            self._get_car_names(offer)

    def print_raport(self):
        msg = 'Average price is {price} PLN\n' \
              'Average mileage is {mileage} km\n' \
              'Average production year is {year}\n' \
              'Most popular car is {car}\n' \
              'Most popular production year is {mp_year}\n' \
              'Most popualr engine type is {engine}\n' \
              'Most popular engine displacement is {engine_displacement} cm3'.format(price=self._calculate_average_price(),
                                                                                    mileage=self._calculate_average_mileage(),
                                                                                    year=self._calculate_average_year(),
                                                                                    car=list(self._get_most_popular_value(self.car_names).keys())[0],
                                                                                    mp_year=list(self._get_most_popular_value(self.prod_years).keys())[0],
                                                                                    engine=list(self._get_most_popular_value(self.fuel_types).keys())[0],
                                                                                    engine_displacement=list(self._get_most_popular_value(self.engine_displacements).keys())[0])
        print(msg)


    def test(self):
        r = requests.get(self.base_url, headers=self.headers).text
        soup = BeautifulSoup(r, "html.parser")
        ul=soup.find_all('select', 'Rodzaj paliwa')
        print(ul)
        with open('source.html', 'w') as f:
            f.write(ul)
        print('TEST')
        print()


if __name__ == "__main__":
    # # o = Otomoto('https://www.otomoto.pl/osobowe/renault/clio/iv-2012/?search%5Border%5D=filter_float_price%3Aasc&search%5Bcountry%5D=')
    # o = Otomoto('https://ria.otomoto.pl/?q=&search%5Bcategory_id%5D=&search%5Border%5D=filter_float_price%3Aasc')
    # o.get_offers()
    # print(len(o.offers))
    # o.get_data()
    #
    # print(o.prices)
    # print(o.mileages)
    # print(o.prod_years)
    # print(o.fuel_types)
    # print(o.engine_displacements)
    # print(o.car_names)
    # print(o._calculate_average_price())
    # print(o._calculate_average_year())
    # print(o._get_most_popular_value(o.engine_displacements))
    # o.print_raport()
    # # o.test()

    start_time = time.time()
    url = sys.argv[1]
    o = Otomoto(url)
    o.get_offers()
    # o.get_data()
    o.print_raport()
    print(time.time()-start_time)