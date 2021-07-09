from avitoParser import AvitoParser
from AvitoTransliterator import Transliterator
from geopy.geocoders import GoogleV3
geolocator = GoogleV3(api_key="AIzaSyCs-97Y3vAIXiP5R0IjXAhYXh3L54qSf3A")
class Query:
    def __init__(self,  chipName: str, sellerRate=None, minCost=None, maxCost=None, sort=None, rad=None):
        self.rad = rad
        self.chipName = chipName
        self.sellerRate = sellerRate
        self.minCost = minCost
        self.maxCost = maxCost
        self.sort = sort

    def makeURL(self, location: str):
        coords = None
        if self.rad is not None:
            loc = geolocator.geocode(location)
            coords = f'{round(loc.latitude, 6)}%2C{round(loc.longitude, 6)}'
        params = {
            's': self.sort,
            'radius': self.rad,
            'pmin': self.minCost,
            'pmax': self.maxCost,
            'q': self.chipName.replace(' ', '+'),
            'geoCoords': coords,
            'p': 1,
        }
        url = f'https://www.avito.ru/{Transliterator.transliterate(location.split()[0])}/tovary_dlya_kompyutera/komplektuyuschie/videokarty-ASgBAgICAkTGB~pm7gmmZw'
        par = []
        for i in params:
            if params[i] is not None:
                par.append(f'{i}={params[i]}')
        return url + '?' + '&'.join(i for i in par)

    def getAds(self, location: str):
        pars = AvitoParser()
        url = self.makeURL(location)
        return pars.getAds(url, self.sellerRate)
