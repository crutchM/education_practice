import data_base
class Adverticement:
    def __init__(self, cost, name, link):
        self.cost = cost
        self.name = name
        self.link = link

    #метод ожидает свой парсер с возможностью воткнуть фильтр

    def show(self):
        return str(self.name) + "\n\n" +  str(self.cost) + "\n\n" +  str(self.link)


