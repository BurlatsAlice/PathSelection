# Path 1-Identifiability Problem

- **Greedy/** contains a Java implementation of the Greedy algorithm.
- **solvers/** contains python interface to run the problem on the *ILP* solver and the *column generation*.
- **instances/** contains various Path 1-Identifiability Problem instances

Running a path selection instance on ILP Solver, Column Generation
--------------------------------------------------------

```
pip install gurobipy # install the requirements
python solvers/main.py [-h] --solver {ilp,column_generation} -i INPUT [-g {cover,1id}] [--timelimit TIMELIMIT] [--solfile SOLFILE] [--csv CSV] [--seed SEED]
```
where ``<ARGS>`` are the argument passed to the model.

The required arguments are :
- ``-i <INSTANCE>`` the instance file, i.e. the file containing the set of routes
- ``-s <SOLVER>`` the solver to use, either ilp, or column_generation
The optional argument are :
- ``--csv <CSV>`` csv file to store the statistics
- ``--solfile <SOLUTION>`` the file to store the solution
- ``--timelimit <TIMELIMIT>`` the timelimit in seconds (default is 180s)
- ``--seed <SEED>`` the used seed

For example to solve the Path 1-Identifiability Problem with the ILP solver:

```python solvers/main.py -i instances/hop_counting_based/zoo/Aarnet.routes --solver ilp```
Note: A Gurobi license is required to run the ILP model, more info [here](https://www.gurobi.com/solutions/licensing/)
Note bis: To run the column generation, verify that you are able to run the Greedy algorithm

Running a path selection on the greedy algorithm
-----------------------------------

```
cd Greedy
mvn install
java -jar target/PathSelection-1.0.jar <ARGS>
```
where ``<ARGS>`` are the argument passed to the model.

The required arguments are :
- ``--routes <ROUTES>`` the instance file, i.e. the file containing the set of routes
The optional arguments are :
- ``--print-stats`` print the stats in the standard output
- ``--write-stats <STATS_FILE>`` print the stats in the given csv file
- ``--print-solution`` print the solution in the standard output
- ``--write-solution <FILE>`` write the solution in the given file
- ``--seed <SEED>`` the used seed


Sources
-------

Gurobi:
>Gurobi Optimization, LLC: Gurobi Optimizer Reference Manual (2023), 
> https://www.gurobi.com
