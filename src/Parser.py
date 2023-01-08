import requests
from bs4 import BeautifulSoup as bs


class Parser:

    def __init__(self, group_id):
        self.URL_TEMPLATE = f'https://vk.com/market-{group_id}'
        self.group_id = group_id

    def parse_goods(self):
        r = requests.get(self.URL_TEMPLATE)
        soup = bs(r.text, "html.parser")
        goods = soup.find_all('div', class_='MarketItems__card')

        return goods

    def get_items_names(self):
        goods = self.parse_goods()
        names = {}
        for item in goods:
            names[f"{self.URL_TEMPLATE}?w={item.a['href'].replace('/', '', 1)}"] = item.div.img['alt']
        return names

    def get_items_links(self):
        goods = self.parse_goods()
        links = []
        for item in goods:
            links.append(f"{self.URL_TEMPLATE}?w={item.a['href'].replace('/', '', 1)}")
        return links


if __name__ == '__main__':
    p = Parser(215897535)
    print(p.get_items_names())
