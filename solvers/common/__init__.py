def hash_pair(a: int, b: int, n: int) -> int:
    """
    Hash a pair of node to link it to its corresponding d_ij
    Depends on the total number of node
    :param a: index of first node
    :param b: index of second node
    :param n: total number of node
    :return: an integer representing the hash
    """
    if a >= n or b >= n : # or a < 0 or b < 0 or a == b:
        raise ValueError('value in pairs cannot be more or equal than n')
    if a < 0 or b < 0:
        raise ValueError('a and b cannot be negative')
    if a == b:
        raise ValueError('a and b cannot be equals')
    if a < b:
        return int((n-1)*(n-2)/2 - (n-a-1)*(n-a-2)/2) + b - 1
    else:
        return int((n-1)*(n-2)/2 - (n-b-1)*(n-b-2)/2 )+ a - 1


def parse_instance(filename: str) -> (int, int, list[set], list[(int, int)]):
    """
    parse instances
    :param filename: the path to the file containing the instance
    :return: a tuple (nodes_number, routes) where nodes_number is an integer representing the number of nodes
            and routes is a list of Route objects containing each available route in the network
    """
    with open(filename, 'r') as input_file:
        lines = input_file.readlines()

    nodes_number = int(lines[0].split(" ")[0])
    routes_number = int(lines[0].split(" ")[1])

    routes = []
    endpoints = []
    for i in range(1, routes_number+1):
        indexes, route_string = lines[i].split(' | ')
        index_a, index_b = indexes.split(" ")
        route = route_string.split(" ")
        routes.append(set([int(node) for node in route]))
        endpoints.append((int(index_a), int(index_b)))

    return nodes_number, routes_number, routes, endpoints


def parse_reductions(filename: str) -> (set[int], list[set[int]], list[int, (int, set[int])], list[list[int]]):
    with open(filename, 'r') as input_file:
        lines = input_file.readlines()

    nbr_indy, nbr_bc, nbr_one_degree_pack, nbr_tail = [int(i) for i in lines[0].strip().split(" ")]

    indy_nodes = set()
    if nbr_indy > 0:
        indy_nodes = set([int(i) for i in lines[1].strip().split(" ")])

    bcs = []
    for line in lines[2: 2 + nbr_bc]:
        bcs.append(set([int(i) for i in line.strip().split(" ")]))

    one_degree_packs = []
    for line in lines[2 + nbr_bc: 2 + nbr_bc + nbr_one_degree_pack]:
        nodes = [int(i) for i in line.strip().split(" ")]
        if len(nodes) > 2:
            one_degree_packs.append((nodes[0], set(nodes[1:])))

    tails = []
    for line in lines[2 + nbr_bc:2 + nbr_bc + nbr_tail]:
        tails.append([int(i) for i in line.strip().split(" ")])

    return indy_nodes, bcs, one_degree_packs, tails


def compute_symptoms(nodes_number: int, routes: list[set]) -> list[set]:
    """
    Compute the symptom of each node from the set of availables routes
    :param nodes_number: the number of nodes
    :param routes: a list of Route objects containing the routes
    :param removed_routes: a set containing the removed routes
    :return: a list of sets containing the symptom of each node
    """
    symptoms = [set() for i in range(nodes_number)]
    for index, route in enumerate(routes):
        for node in route:
            symptoms[node].add(index)

    return symptoms

