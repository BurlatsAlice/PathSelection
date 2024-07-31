import sys
from problems import PathSelectionProblem
from models import PSPIntegerLinearProgram, PSPColumnGeneration
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--solver',
                        required=True,
                        choices=["ilp", "column_generation"],
                        default="ilp")
    parser.add_argument('-i', '--input',
                        help="instance file",
                        required=True)
    parser.add_argument('-g', '--goal',
                        help="goal of model",
                        choices=["cover", "1id"],
                        default="1id")
    parser.add_argument('--timelimit', required=False, type=float , default=180.0,
                        help="time limit for solving problem")
    parser.add_argument('--solfile', required=False, type=str, help='path to store solution')
    parser.add_argument('--csv', required=False, type=str, help="csv file to store stats")
    parser.add_argument('--seed', type=int, default=1863947)

    args = parser.parse_args()

    try:
        problem = PathSelectionProblem(args.input, args.goal)
    except FileNotFoundError:
        print(f"{args.input} does not exist")
        exit()

    print("Loading model")
    if args.solver == "ilp":
        solver = PSPIntegerLinearProgram(problem, args.seed)
    elif args.solver == 'column_generation':
        solver = PSPColumnGeneration(problem, args.seed)
    else:
        print("Please enter a valid solver")
        exit()

    print("Building model")
    solver.build_model()
    print("Solving instance")
    solver.solve(args.timelimit)
    print("Instance solved, retrieving stats")

    if args.solfile:
        problem.write_solution(args.solfile, solver.get_solution())

    if args.csv:

        # Name;Solver;Goal;Reductions;N_Paths;SolvingTime(s);TotalTime(s);Status;IsCovered;IsOne1id
        output = (f"{args.input};{args.solver};{args.goal};{args.seed};{args.reductions != ''};{solver.get_objective()};"
                  f"{solver.get_solving_time()};{solver.get_total_time()};{solver.get_status()};"
                  f"{problem.is_covered(solver.get_solution())};{problem.is_one_id(solver.get_solution())};"
                  f"{args.timelimit};{len(problem.get_sources(solver.get_solution()))};")
        sources_sol = problem.get_sources(solver.get_solution()).values()
        if len(sources_sol) > 0:
            output += f"{max(problem.get_sources(solver.get_solution()).values())}"
        else:
            output += "-1"
        if isinstance(solver, PSPIntegerLinearProgram):
            output += f";{solver.mip_gap}"
        if isinstance(solver, PSPColumnGeneration):
            output += (f";{solver.greedy_time};{solver.cg_time};{solver.conversion_time};"
                       f"{solver.greedy_obj};{solver.column_nbr};"
                       f"{solver.lp_solution_cost};{solver.int_lp_solution_cost};{solver.iterations};{solver.avg_null_cover_dual};{solver.avg_null_1id_dual}")
        with open(args.csv, "a") as csvfile:
            print(output, file=csvfile)
    else:
        print(
            f"Status : {solver.get_status()}\n"
            f"Number of paths : {solver.get_objective()}\n"
            f"Number of sources : {len(problem.get_sources(solver.get_solution()))}\n"
            f"Maximal load on source : {max(problem.get_sources(solver.get_solution()).values())}\n"
            f"Covered : {problem.is_covered(solver.get_solution())}\n"
            f"1id : {problem.is_one_id(solver.get_solution())}\n"
            f"Solving Time (s) : {solver.get_solving_time()}\n"
            f"Total Time (s) : {solver.get_total_time()}")

        problem.print_solution(solver.get_solution())
