from query import Query

class User(object):
    def __init__(self, role, id, favourites, queries, location):
        self.role = role
        self.id = id
        self.favourites = favourites
        self.queries = queries
        self.location = location


    def makeQuery(self, rad, chipName, sellerRate, minCost, maxCost, sort):
        return Query(rad, chipName, sellerRate, minCost, maxCost, sort)




