import time
import concurrent.futures
import bs4.element
import requests
from bs4 import BeautifulSoup
from Ad import Advertisement
import concurrent.futures
import concurrent.futures.thread


def getProxies():
    for i in ['https://www.sslproxies.org/', 'https://free-proxy-list.net/']:
        r = requests.get(i)
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('tbody')
        proxies = []
        for row in table:
            if True:#row.find_all('td')[4].text =='elite proxy':
                proxy = ':'.join([row.find_all('td')[0].text, row.find_all('td')[1].text])
                proxies.append(proxy)
            else:
                pass
    return proxies


def extract(pUrl):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 YaBrowser/21.6.0.616 Yowser/2.5 Safari/537.36'}
    pr = 'http://' + pUrl[0]
    try:
        r = requests.get(pUrl[1], headers=headers, proxies={'http' : pr,'https': pr}, timeout=3)
        if r.status_code == 200:
            return r
    except:
        pass



def getResponse(url: str):
    # global _url
    # _url = url
    resp = []
    while True:
        proxylist = ((i, url) for i in getProxies())
        with concurrent.futures.ThreadPoolExecutor(max_workers=5000) as executor:
            res = [executor.submit(extract, i) for i in proxylist]


            for r in concurrent.futures.as_completed(res):
                if r.result() is not None:
                    print(r.result().status_code)
                    executor.shutdown(wait=False)
                    resp.append(r)
                    return resp[0].result()

class AvitoParser:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 YaBrowser/21.6.0.616 Yowser/2.5 Safari/537.36',
            'Accept-Language': 'ru',
        }

    def isAvailable(self, url):
        r = getResponse(url)
        warn = BeautifulSoup(r.text, 'lxml').select('a.item-closed-warning')
        return True if not warn else False

    def getAdsCount(self, soup: BeautifulSoup):
        pc = soup.select_one('span.page-title-count-1oJOc')
        return int(pc.string.strip()) if pc is not None else 0

    def getAds(self, url: str, sellerRating: float):
        soup = BeautifulSoup(getResponse(url).text, 'lxml')
        ad_count = self.getAdsCount(soup)
        pages_count = 1

        ad_c = ad_count
        while True:
            ads = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                ads = list(executor.map(self.parseAd, soup.select('div.iva-item-root-G3n7v.photo-slider-slider-3tEix.iva-item-list-2_PpT')))
            if sellerRating is not None:
                tempads = ((i, sellerRating) for i in ads)
                with concurrent.futures.ThreadPoolExecutor(max_workers=70) as executor:
                    ads = list(executor.map(self.ratingFilter, tempads))
            ads = [ad for ad in ads if ad is not None]
            if ad_c > 50:
                yield ads
            else:
                yield ads[:ad_c]
                break
            #time.sleep(random.randint(7, 12))
            pages_count += 1
            cur_url = url[:-1] + str(pages_count)
            ad_c -= 50
            soup = BeautifulSoup(getResponse(cur_url).text, 'lxml')

    def parseAd(self, ad: bs4.element.Tag):
        link = ad.select_one('a.link-link-39EVK')
        href = 'https://www.avito.ru' + link.get('href')
        name = link.select_one('h3.title-root-395AQ.iva-item-title-1Rmmj.title-listRedesign-3RaU2').string.strip()
        price = self.getPrice(ad, "price-text-1HrJ_ text-text-1PdBw text-size-s-1PUdo")
        return Advertisement(cost=price, name=name, link=href)

    def getPrice(self, ad: bs4.element.Tag, cls: str):
        return self.cleanPrice(ad.find('span', {"class" : cls}).text)

    def cleanPrice(self, price):
        if price == 'Цена не указана':
            return None
        if price == 'Бесплатно':
            return 0
        return int(''.join(i for i in price if i.isdigit()))

    def ratingFilter(self, adRate):
        ad = adRate[0]
        rating = adRate[1]
        r = getResponse(ad.link)
        rate = BeautifulSoup(r.text, 'lxml').select_one('div.seller-info-col')
        if rate is None:
            return None
        rate = rate.find('span', {"class" : "seller-info-rating-score"})
        if rate is None:
            return None
        return ad if float(rate.text.strip().replace(',', '.')) >= rating else None


    def parsePrice(self, url: str):
        r = getResponse(url)
        price = BeautifulSoup(r.text, 'lxml').select_one('div.price-value.price-value_side-card')
        price = self.getPrice(price, "js-item-price")
        return price

    def getResponse(self, url):
        return getResponse(url)
