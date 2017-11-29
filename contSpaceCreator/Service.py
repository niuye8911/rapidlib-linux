class Node:
    def __init__(self, node_name, cost, mv):
        self.name = node_name
        self.cost = cost
        self.mv = mv

    def get_name(self):
        return self.name

    def get_cost(self):
        return self.cost

    def get_mv(self):
        return self.mv


class Service:
    def __init__(self, name):
        self.name = name
        self.nodes = []

    def get_nodes(self):
        return self.nodes

    def get_name(self):
        return self.name

    def add_node(self, node):
        self.nodes.append(node)