import copy
import random
from gurobipy import GRB
from common import hash_pair
from time import time
from problems import PathSelectionProblem
import gurobipy as gp

MEM_LIMIT = 20
RANDOM_SEED = 1863947
DEFAULT_TIMEOUT = 1800


class Node:
    instance: PathSelectionProblem
    used_routes: set[int]
    routes_init: set[int]

    branching_constraints_description: list

    finished: bool
    solution: dict
    description: str
    timelimit: float
    start_time: float
    iterations: int
    avg_null_cover_dual: float
    avg_null_1id_dual: float

    def __init__(self, instance: PathSelectionProblem, used_routes: set[int], timelimit: int, description: str = "",
                 seed=RANDOM_SEED):
        self.instance = instance
        self.used_routes = used_routes
        self.routes_init = copy.copy(used_routes)
        # print(self.used_routes)
        # self.forbidden_routes = forbidden_routes
        self.timelimit = float(timelimit)

        self.finished = False

        self.solution = {}
        self.objective_value = -1
        self.iterations = -1
        self.avg_null_cover_dual = -1.0
        self.avg_null_1id_dual = -1.0

        self.description = description

        env = gp.Env(empty=True)
        env.setParam('OutputFlag', 0)
        env.start()
        self.model = gp.Model("RMP", env=env)
        self.timelimit = max(timelimit, 0)
        self.model.setParam('TimeLimit', self.timelimit)
        self.model.setParam('SoftMemLimit', MEM_LIMIT)
        self.model.setParam('Seed', seed)
        self.model.setParam('LogToConsole', 0)
        random.seed(seed)

        self.branching_constraints_stack = []

    def init_rmp(self):
        self.model.setParam(GRB.Param.Threads, 1)
        self.model.setParam('SoftMemLimit', MEM_LIMIT)
        self.model.setParam('Seed', RANDOM_SEED)

        route_vars = self.model.addVars([i for i in self.used_routes], name="Y",
                                        vtype=GRB.CONTINUOUS)

        # objective function : minimize the sum of the routes var
        self.model.setObjective(gp.quicksum(route_vars), GRB.MINIMIZE)

        # cover constraints
        for node in range(self.instance.node_number):
            constraint = [l for l in self.instance.symptoms[node] if l in self.used_routes]

            self.model.addConstr(
                gp.quicksum([route_vars[l] for l in constraint]) >= 1,
                name=str(node))

        # one id constraints
        if self.instance.goal == '1id':
            for i in range(self.instance.node_number):
                for j in range(i + 1, self.instance.node_number):
                    full_constraint = (self.instance.symptoms[i]
                                       .symmetric_difference(self.instance.symptoms[j]))
                    constraint = [l for l in full_constraint if l in self.used_routes]

                    self.model.addConstr(
                        gp.quicksum([route_vars[l] for l in constraint]) >= 1,
                        name=str(self.instance.node_number + hash_pair(i, j, self.instance.node_number)))

        self.model.update()

    def solve_rmp(self):
        self.model.optimize()

        # if model is infeasible
        if self.model.status == 3:
            print("model is infeasible")
            return None

        self.objective_value = self.model.getObjective().getValue()

        # retrieval of the solution of the dual problem
        # one value for each node due to cover constraints
        # if goal is 1-id then there is also 1 value for each pair of nodes
        constraints = self.model.getConstrs()
        dual_values = [0.0 for i in range(len(constraints))]

        self.solution = {}
        for route in self.used_routes:
            if self.model.getVarByName(f"Y[{route}]").getAttr("X") != 0:
                self.solution[route] = self.model.getVarByName(f"Y[{route}]").getAttr("X")

        for c in constraints:
            dual_values[int(c.constrName)] = c.getAttr("Pi")
        return dual_values

    def update_rmp(self, routes_to_add):
        constraints = self.model.getConstrs()
        columns = {}
        for route in routes_to_add:
            columns[route] = set()

        for node in range(self.instance.node_number):
            temp_symptom = self.instance.symptoms[node].intersection(routes_to_add)
            for route_index in temp_symptom:
                columns[route_index].add(node)

            if self.instance.goal == '1id':
                for node_b in range(node, self.instance.node_number):
                    for route_index in temp_symptom.symmetric_difference(
                            self.instance.symptoms[node_b].intersection(routes_to_add)):
                        columns[route_index].add(
                            self.instance.node_number + hash_pair(node, node_b, self.instance.node_number))

        for index, (constr, constr_type) in enumerate(reversed(self.branching_constraints_stack)):
            for route_index in constr.intersection(routes_to_add):
                columns[route_index].add(len(self.model.getConstrs()) - (index + 1))

        for route in routes_to_add:
            self.model.addVar(name=f"Y[{route}]", vtype=GRB.CONTINUOUS,
                              column=gp.Column([1.0 if i in columns[route] else 0.0 for i in range(len(constraints))],
                                               constraints), obj=1.0)
            self.used_routes.add(route)
        self.model.update()


    def solve_pricing(self, dual_values, columns_number=10):
        """
        Solve the pricing problem, i.e. find the removed route with highest price
        :param dual_values: optimal solution of the current dual problem
        :return: index of the best route in the global route set (int) and its reduced cost (int)
        """
        forbidden_routes = set()
        for constr, constr_type in self.branching_constraints_stack:
            if constr_type is False:
                forbidden_routes = forbidden_routes.union(constr)

        prices = [[i, 0.0] for i in range(self.instance.route_number)]

        # cost linked to cover constraints
        # if a route crosses a node, the cost corresponding to this node cover constraint
        # will be added to the route cost
        # as the majority of the dual values are equal to zero, it is more efficient to
        # iterate over the non-zero node costs than on the routes themselves
        # print(dual_values)
        null_cover_dual = 0.0
        for node in range(self.instance.node_number):
            if dual_values[node] != 0:
                for route in self.instance.symptoms[node]:
                    prices[route][1] += dual_values[node]
            else:
                null_cover_dual += 1.0

        # cost linked to 1id constraints
        # if a route crosses one of the two nodes in a pair and not the other one
        # then the cost linked to this pair's distinguishability constraint is added to the route
        # again, we iterate over the pair of nodes rather than the routes themselves
        null_1id_dual = 0.0
        if self.instance.goal == "1id":
            for node_a in range(self.instance.node_number):
                for node_b in range(node_a + 1, self.instance.node_number):
                    val = dual_values[self.instance.node_number + hash_pair(node_a, node_b, self.instance.node_number)]
                    if val != 0:
                        for route_index in self.instance.symptoms[node_a].symmetric_difference(
                                self.instance.symptoms[node_b]):
                            prices[route_index][1] += val
                    else:
                        null_1id_dual += 1.0

        for index, (branching_constr, constr_type) in enumerate(reversed(self.branching_constraints_stack)):
            for route in branching_constr.difference(self.used_routes):
                if constr_type:
                    prices[route][1] += dual_values[-(index + 1)]

        self.avg_null_cover_dual = self.avg_null_cover_dual*(self.iterations)
        self.avg_null_cover_dual += null_cover_dual
        self.avg_null_cover_dual = self.avg_null_cover_dual/(self.iterations+1.0)

        self.avg_null_1id_dual = self.avg_null_1id_dual*(self.iterations)
        self.avg_null_1id_dual += null_1id_dual
        self.avg_null_1id_dual = self.avg_null_1id_dual/(self.iterations+1.0)

        var_to_add = set()
        prices = sorted(prices, key=lambda x: x[1], reverse=True)

        for i in range(len(prices)):
            if prices[i][1] <= 1:
                break
            if prices[i][0] not in self.used_routes and prices[i][0] not in forbidden_routes:
                var_to_add.add(prices[i][0])
                if len(var_to_add) == columns_number:
                    break
        # print(var_to_add)
        return var_to_add

    def solve(self, columns_number=10):
        """
        Solve the path selection problem using column generation
        """
        self.iterations = 0
        self.start_time = time()
        # self.init_rmp()
        dual_values = self.solve_rmp()

        # if model is infeasible
        if self.model.status == 3:
            # print("Infeasible model")
            # print(self.get_missing_variables())
            return


        new_routes = self.solve_pricing(dual_values, columns_number)
        self.iterations = 1
        while len(new_routes) > 0 and self.timelimit > 0:
            self.used_routes = self.used_routes.union(new_routes)
            self.update_rmp(new_routes)

            self.timelimit = max(self.timelimit, 0.0)
            self.model.setParam('TimeLimit', self.timelimit)
            self.start_time = time()

            dual_values = self.solve_rmp()

            new_routes = self.solve_pricing(dual_values)
            self.timelimit = self.timelimit - (time() - self.start_time)

            if len(new_routes) == 0:
                self.finished = True
            self.iterations += 1

    def solve_ilp(self):
        """
        Solve the ILP version of the problem
        :return: a set containing the index of the routes used as measurement paths
        """
        # convert continuous variables into binary variables
        for v in self.model.getVars():
            v.vtype = GRB.BINARY

        # the optimal solution of the LP relaxation is used as a lower bound on the objective function
        self.model.addConstr(gp.quicksum(self.model.getVars()) >= self.objective_value)
        self.model.update()
        self.timelimit = self.timelimit - (time() - self.start_time)

        self.timelimit = max(self.timelimit, 0.0)
        self.model.setParam('TimeLimit', self.timelimit)

        self.model.optimize()

        self.objective_value = self.model.getObjective().getValue()
        self.solution = {}
        for route in self.used_routes:
            if self.model.getVarByName(f"Y[{route}]").getAttr("X") != 0:
                self.solution[route] = self.model.getVarByName(f"Y[{route}]").getAttr("X")
        if self.model.status != 2:
            self.finished = False
