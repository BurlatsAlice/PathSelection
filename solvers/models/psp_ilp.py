from problems import PathSelectionProblem
from gurobipy import GRB
import gurobipy as gp
import logging

MEM_LIMIT = 50
DEFAULT_TIMEOUT = 1800
RANDOM_SEED = 1863947

STATUS_CODE = {2: "Optimality", 3: "Infeasible", 9: "Timeout", 17:"MEM_LIMIT"}


class PSPIntegerLinearProgram:
    instance: PathSelectionProblem
    env: gp.Env
    model: gp.Model
    solution: dict[int, float]
    status: str
    solving_time: float
    total_time: float
    objective_value: float
    mip_gap: float

    def __init__(self, instance: PathSelectionProblem, seed: int):
        self.logger = logging.getLogger('ILP')
        self.logger.setLevel(logging.INFO)

        self.instance = instance
        self.env = gp.Env(empty=True)
        self.env.setParam('OutputFlag', 0)
        self.env.start()
        self.model = gp.Model("ILP Model", env=self.env)
        self.model.setParam('TimeLimit', DEFAULT_TIMEOUT)
        self.model.setParam('SoftMemLimit', MEM_LIMIT)
        self.model.setParam('Seed', seed)
        self.model.setParam(GRB.Param.Threads, 1)

        self.solution = {}
        self.objective_value = instance.route_number
        self.status = "Not run"
        self.solving_time = -1.0
        self.total_time = -1.0

    def build_model(self):

        # y[i] == 1 iff route i is a measurement path, 0 otherwise
        y = self.model.addVars([i for i in self.instance.get_routes_set()],
                               name="Y",
                               vtype=GRB.BINARY)

        # objective : minimize the number of measurement paths
        self.model.setObjective(gp.quicksum(y), GRB.MINIMIZE)

        # each node must be crossed by at least one measurement path
        for node in self.instance.get_node_set():
            self.model.addConstr(gp.quicksum([y[l] for l in self.instance.get_symptom(node)]) >= 1, name=str(node))

        if self.instance.goal == "1id":

            for i in set(range(self.instance.node_number)):
                for j in set(range(i + 1, self.instance.node_number)):
                    self.model.addConstr(
                        gp.quicksum(
                            [y[l] for l in self.instance.get_symptom(i).symmetric_difference(self.instance.get_symptom(j))])
                        >= 1)

    def solve(self, time_limit: float):
        self.model.setParam('TimeLimit', time_limit)
        self.model.optimize()

        if self.model.status == 3:
            print(self.get_status())
            return

        try:
            self.objective_value = self.model.getObjective().getValue()
        except AttributeError:
            self.objective_value = -1
        
        try:
            self.mip_gap = self.model.MIPGap
        except AttributeError:
            self.mip_gap = -1
        self.solution = {}

        for index in range(self.instance.route_number):
            try:
                if self.model.getVarByName(f"Y[{index}]").getAttr("X") > 0:
                    self.solution[index] = self.model.getVarByName(f"Y[{index}]").getAttr("X")
            except AttributeError:
                pass

        self.logger.debug(self.solution)
        self.logger.debug(self.objective_value)

    def get_objective(self):
        return self.objective_value

    def get_status(self):
        return STATUS_CODE[self.model.status]

    def get_solving_time(self):
        return self.model.getAttr("Runtime")

    def get_total_time(self):
        return None

    def get_solution(self):
        return self.solution
