import time
import random
import bs4.element
import requests
from bs4 import BeautifulSoup
from Ad import Adverticement

class AvitoParser:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 YaBrowser/21.6.0.616 Yowser/2.5 Safari/537.36',
            'Accept-Language': 'ru',
        }

    def isAvailable(self, url):
        r = self.session.get(url)
        warn = BeautifulSoup(r.text, 'lxml').select('a.item-closed-warning')
        return True if not warn else False

    def getAdsCount(self, soup: BeautifulSoup):
        pc = soup.select_one('span.page-title-count-1oJOc')
        return int(pc.string.strip()) if pc is not None else 0

    def getAds(self, url: str, func):
        cur_url = url
        soup = BeautifulSoup(self.session.get(url).text, 'lxml')
        ad_count = self.getAdsCount(soup)
        pages_count = 1

        ad_c = ad_count
        while True:
            ads = []
            for ad in soup.select('div.iva-item-root-G3n7v.photo-slider-slider-3tEix.iva-item-list-2_PpT'):
                cur_ad = func(ad)
                if cur_ad is not None:
                    ads.append(cur_ad)
            if ad_c > 50:
                yield ads
            else:
                yield ads[:ad_c]
                break
            time.sleep(random.randint(7, 12))
            pages_count += 1
            cur_url = url[:-1] + str(pages_count)
            ad_c -= 50
            soup = BeautifulSoup(self.session.get(cur_url).text, 'lxml')

    def parseAd(self, ad: bs4.element.Tag, filter=lambda x: True):
        link = ad.select_one('a.link-link-39EVK')
        href = 'https://www.avito.ru' + link.get('href')
        if not filter(href):
            return
        name = link.select_one('h3.title-root-395AQ.iva-item-title-1Rmmj.title-listRedesign-3RaU2').string.strip()
        g= ad.find('span', {"class" : "price-text-1HrJ_ text-text-1PdBw text-size-s-1PUdo"}).text
        price = self.getPrice(ad)
        return Adverticement(cost=price, name=name, link=href)

    def getPrice(self, ad: bs4.element.Tag):
        return self.cleanPrice(ad.find('span', {"class" : "price-text-1HrJ_ text-text-1PdBw text-size-s-1PUdo"}).text)

    def cleanPrice(self, price):
        if price == 'Цена не указана':
            return None
        if price == 'Бесплатно':
            return 0
        return int(''.join(i for i in price if i.isdigit()))

    def ratingFilter(self, href, rating: float):
        time.sleep(random.randint(10, 15))
        r = self.session.get(href)
        rate = BeautifulSoup(r.text, 'lxml').select_one('div.seller-info-col')
        rate = rate.find('span', {"class" : "seller-info-rating-score"})
        if rate is None:
            return False
        return True if float(rate.text.strip().replace(',', '.')) >= rating else False







