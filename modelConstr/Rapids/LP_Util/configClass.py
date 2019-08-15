class RAPIDConfig:
    def __init__(self, services, cost):
        self.services = services
        self.cost = cost

    def get_nodes(self):
        return self.services

    def get_cost(self):
        return self.cost

    def print_yourself(self):
        res = ""
        for i in self.services:
            res += i.print_in_constraint()
            res += " "
        return res


class RSDGNode(object):
    def __init__(self, service_name, level):
        self.service = service_name
        self.level = level
        self.cost = 0

    def print_in_constraint(self):
        return str(self.service) + "_" + str(self.level)

    def update_cost(self, cost):
        self.cost = cost
