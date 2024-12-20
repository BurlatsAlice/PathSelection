from time import time
from problems import PathSelectionProblem
from models import Node
from models import get_greedy_psp_solution_routes


class PSPColumnGeneration:
    instance: PathSelectionProblem
    lp_solution_cost: float
    int_lp_solution_cost: int
    solving_time: float
    greedy_time: float
    cg_time: float
    conversion_time: float
    status: str
    seed: int
    column_nbr: int
    greedy_obj: int

    def __init__(self, instance: PathSelectionProblem,
                 seed=784646):
        self.instance = instance
        self.objective = -1
        self.solution = None
        self.solving_time = -1.0
        self.greedy_time = -1.0
        self.cg_time = -1.0
        self.conversion_time = -1.0
        self.column_nbr = -1
        self.greedy_obj = -1
        self.seed = seed
        self.int_lp_solution_cost = -1
        self.lp_solution_cost = -1
        self.iterations = -1
        self.avg_null_1id_dual = -1.0
        self.avg_null_cover_dual = -1.0

    def solve(self, timelimit):
        self.solution, self.greedy_time = get_greedy_psp_solution_routes(self.instance, self.seed)
        self.greedy_obj = len(self.solution)
        self.objective = len(self.solution)
        self.status = "Greedy"
        start_time = time()

        node = Node(self.instance, set(self.solution.keys()), timelimit, "root", self.seed)
        node.init_rmp()
        node.solve()
        self.cg_time = time() - start_time
        self.column_nbr = len(node.used_routes)
        self.avg_null_1id_dual = node.avg_null_1id_dual
        self.avg_null_cover_dual = node.avg_null_cover_dual

        if not node.finished:
            self.status = "CG_unfinished"
        else:
            self.status = "CG"

        self.lp_solution_cost = node.objective_value
        self.int_lp_solution_cost = sum(node.solution.values())
        self.iterations = node.iterations

        if time() - start_time > timelimit:
            self.solving_time = time() - start_time + self.greedy_time
            return

        node.solve_ilp()
        if node.finished:
            self.status = "Completed"

        self.conversion_time = time() - start_time - self.cg_time

        self.solving_time = time() - start_time + self.greedy_time
        self.objective = node.objective_value
        self.solution = node.solution

    def build_model(self):
        pass

    def get_objective(self):
        return self.objective

    def get_status(self):
        return self.status

    def get_solving_time(self):
        return self.solving_time

    def get_total_time(self):
        return None

    def get_solution(self):
        return self.solution

    def get_column_number(self):
        return self.column_nbr
