class Query:
    def __init__(self, rad, chipName, sellerRate, minCost, maxCost, sort):
        self.rad = rad
        self.chipName = chipName
        self.sellerRate = sellerRate
        self.minCost = minCost
        self.maxCost = maxCost
        self.sort = sort

   #метод ожидает свой парсер с возможностью воткнуть фильтр