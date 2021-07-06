class User:
    def __init__(self, id, location, role, regDate):
        self.id = id
        self.location = location
        self.role = role
        self.regDate = regDate


    def getLastQuery(self):
        pass
        #здесь подтянем метод из контроллера с self.Id


    def getInfo(self):
        return "ID: {0}, Местоположение: {1}, Роль: {2}, Дата регистрации: {3}".format(self.id, self.location, self.role, self.regDate)

