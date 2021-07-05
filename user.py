from Query import Query
import data_base

class User(object):
    def __init__(self, role, id, register_date, favourites, queries, location, query):
        self.role = role
        self.id = id
        self.favourites = favourites
        self.queries = queries
        self.location = location
        self.reg_date = register_date
        self.query = query

    def makeQuery(self, rad, chipName, sellerRate, minCost, maxCost, sort):
        return Query(rad, chipName, sellerRate, minCost, maxCost, sort)






