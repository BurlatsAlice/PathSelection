from problems import PathSelectionProblem
import subprocess
import os


def get_greedy_psp_solution_routes(instance: PathSelectionProblem, seed: int):
    solution_endpoints, greedy_time = get_greedy_psp_solution_endpoints(instance.source_file, instance.goal, seed)
    solution = {}
    for pair in solution_endpoints:
        for index, (src, dest) in enumerate(instance.endpoints):
            if int(pair[0]) == src and int(pair[1]) == dest:
                solution[index] = 1.0
                break

    return solution, greedy_time


def get_greedy_psp_solution_endpoints(route_file, goal, seed: int):
    greedy_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Greedy/target/PathSelection-1.0.jar")
    output = subprocess.getoutput(
        f"java -Xmx20g -jar {greedy_path} --routes {route_file} "
        f"--print-solution --seed {seed}") #65543
    # print(output)
    lines = output.split("\n")
    time_greedy = float(lines[0].strip())
    n = int(lines[1].strip())

    indexes = []
    for line in lines[2:]:
        endpoints, nodes = line.split(" | ")
        src, dest = endpoints.strip().split(" ")
        indexes.append((src, dest))

    return indexes, time_greedy
