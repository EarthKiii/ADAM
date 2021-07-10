import requests
import json
import unidecode
from bs4 import BeautifulSoup
import copy


class Item(object):
    def __init__(self, in_list_id, title, description, url, deal_type, merchant_name, product_image, prime, free_shipping, price):
        self.in_list_id = in_list_id
        self.title = title
        self.description = description
        self.url = url
        self.deal_type = deal_type
        self.merchant_name = merchant_name
        self.product_image = product_image
        self.prime = prime
        self.free_shipping = free_shipping
        self.price = price


def search(keywords: list = [""], price_fork: list = [0, 999999]):
    if len(price_fork) != 2:
        raise ValueError("Wrong length given for list : excepted 2")
    for float_ in price_fork :
        if not isinstance(float_, int):
            raise TypeError("Price fork must contain integers")
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
    headers = {'User-Agent': user_agent}
    error = False
    list_items = []
    page, increment = 0, 1
    [unidecode.unidecode(keyword.lower()) for keyword in keywords]
    while not error:
        html_text = requests.get(f'https://www.amazon.fr/gp/goldbox/ref=sxts_snpl_1_1_5f9bf52a-7813-4149-a328-db194d6ed9e6?pf_rd_p=5f9bf52a-7813-4149-a328-db194d6ed9e6&pf_rd_r=SEC4QV785RV925CM5BKK' +
                                 f'&pd_rd_wg=P5xjR&pd_rd_w=Y6nLm&qid=1625584165&pd_rd_r=d896263f-0f6d-4b7f-86f9-70e6f552fe67&deals-widget=%257B%2522version%2522%253A1%252C%2522viewIndex%2522%253A' +
                                 f'{page}%252C%2522presetId%2522%253A%25225CE95CF0C7CE703078D21C059FE6936D%2522%252C%2522sorting%2522%253A%2522BY_SCORE%2522%257D', headers=headers).text
        soup = BeautifulSoup(html_text, 'html.parser')
        try:
            data = copy.deepcopy(list(json.loads(soup.find_all('script')[75].text.split('"dealDetails":', 1)[1].rsplit(',"dealStatus":{"', 1)[0]).values()))
        except IndexError:
            error = True
        for index_item, item in enumerate(data):
            try:
                item_price = data[index_item]["maxCurrentPrice"]
            except KeyError:
                item_price = -1
            try:
                merchant = data[index_item]["merchantName"]
            except KeyError:
                merchant = "Unknown"
            item_desc = unidecode.unidecode(data[index_item]["description"].lower())
            item_title = unidecode.unidecode(data[index_item]["title"].lower())
            if (all(keyword in item_desc for keyword in keywords) or all(keyword in item_title for keyword in keywords)) and (item_price == -1 or (item_price > price_fork[0] and item_price < price_fork[1])):
                list_items.append(Item(in_list_id=data.index(item), title=data[index_item]["title"],
                                       description=data[index_item]["description"], url=data[index_item]["egressUrl"],
                                       deal_type=data[index_item]["type"], merchant_name=merchant,
                                       product_image=data[index_item]["primaryImage"], prime=data[index_item]["isPrimeEligible"],
                                       free_shipping=data[index_item]["isEligibleForFreeShipping"], price=item_price))
        page += 60
    return list_items
