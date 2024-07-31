from common import parse_instance, compute_symptoms

class PathSelectionProblem:
    node_number: int
    route_number: int
    symptoms: list[set]
    goal: str
    endpoints: list[(int, int)]
    initial_route_number: int

    def __init__(self, file_path: str, goal: str) -> None:
        self.source_file = file_path
        (self.node_number,
         self.route_number,
         routes,
         self.endpoints) = parse_instance(file_path)
        self.goal = goal
        self.initial_route_number = len(routes)

        self.symptoms = compute_symptoms(self.node_number, routes)
        # print("symptoms computed")

    def is_covered(self, solution: dict) -> bool:
        for index, symptom in enumerate(self.symptoms):
            coverage = 0
            for route in symptom.intersection(solution.keys()):
                coverage += solution[route]
            if coverage == 0:
                return False
        return True

    def is_one_id(self, solution: dict) -> bool:
        for i in range(self.node_number):
            for j in range(i + 1, self.node_number):
                one_identifiability = 0
                for route in self.symptoms[i].symmetric_difference(self.symptoms[j]).intersection(solution.keys()):
                    one_identifiability += solution[route]
                if one_identifiability < 1:
                    return False
        return True

    def get_route(self, route_index: int) -> set[int]:
        route = set()
        for node, symptom in enumerate(self.symptoms):
            if route_index in symptom:
                route.add(node)
        return route

    def get_sources(self, solution: dict) -> dict:
        sources = {}  # {source_id: load}
        for route in solution.keys():
            current_source = self.endpoints[route][0]
            if current_source not in sources.keys():
                sources[current_source] = 0
            sources[current_source] += 1
        return sources

    def write_solution(self, sol_path: str, solution: dict) -> None:
        output_string = f"{self.node_number}\n"
        for index, val in solution.items():
                output_string += f"{self.endpoints[index][0]} {self.endpoints[index][1]} |"
                for node in self.get_route(index):
                    output_string += f" {node}"
                # output_string += "{} | {} {}\n".format(self.endpoints[index], self.get_route(index), val)
                output_string += "\n"
        with open(sol_path, "w") as file:
            file.write(output_string)

    def get_routes_set(self):
        return set(range(self.route_number))

    def get_node_set(self):
        return set(range(self.node_number))

    def get_symptom(self, node: int):
        return self.symptoms[node]

    def get_endpoints(self, route_index):
        return self.endpoints[route_index]

    def get_number_removed_routes(self):
        return self.initial_route_number - self.route_number

    def print_solution(self, solution: dict):
        for route, val in solution.items():
            print("{} : {}; {} ({})".format(val, self.endpoints[route], self.get_route(route), route))
