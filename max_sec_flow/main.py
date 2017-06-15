from gurobipy import *
from secure_path import secure_path
from secure_path_sumvio import secure_path_sumvio
from secure_path_minviobound import secure_path_minviobound
import random
from result_evaluation import visualize_results
from result_evaluation import visualize_misses

def generateGraph(nodes, arcs):
    graph={}
    cap_graph={}
    max_rule_graph = {}
    init_max_rule = 0

    for n in nodes:
        if not graph.has_key(n):
            graph[n] = {}
            cap_graph[n] = {}

        for m in nodes:
            if (n,m) in arcs:
                graph[n][m] = 1
                cap_graph[n][m] = 10
        max_rule_graph[n] = init_max_rule

    return graph, cap_graph, max_rule_graph

def getGraph():

    #Model data
    #fname="/home/stefan/Desktop/FLIP/Rocketfuel/3967/weights.intra"
    fname = "/home/stefan/Desktop/FLIP/Rocketfuel/1239/weights.intra"

    capac = 10

    nodes = []
    arcs = []
    capacity = {}
    cost = {}

    with open(fname) as f:
        content = f.readlines()
        for line in content:
            e = line.split(" ")
            if e[0] not in nodes:
                nodes.append(e[0])
            if e[1] not in nodes:
                nodes.append(e[1])
            arcs.append((e[0], e[1]))
            capacity[(e[0], e[1])] = capac
            cost[(e[0], e[1])] = float(e[2])
    arcs = tuplelist(arcs)

    graph, cap_graph, max_rule_graph = generateGraph(nodes, arcs)

    return graph, capacity, max_rule_graph, nodes, arcs

def calc_sec_category(categories):
    A = int(categories[0]) * pow(2, 4)
    B = int(categories[1]) * pow(2, 3)
    C = int(categories[2]) * pow(2, 2)
    D = int(categories[3]) * pow(2, 1)
    E = int(categories[4]) * pow(2, 0)
    return A+B+C+D+E

def get_security_class(secclass):
    if secclass=='Public':
        return 1
    elif secclass=='Classified':
        return 2
    elif secclass=='Secret':
        return 3
    elif secclass=='Top Secret':
        return 4
    else:
        return 1

def get_rand_secclass():
    randsc = random.randint(1,100)
    #return 1
    if randsc > 0 and randsc <= 25:
        return 1  # Public
    elif randsc > 25 and randsc <= 50:
        return 2  # Classified
    elif randsc > 50 and randsc <= 75:
        return 3  # Secret
    elif randsc > 75 and randsc <= 100:
        return 4  # Top Secret

def get_rand_seccategory():
    randsc = random.randint(1,100)
    #return 1
    if randsc > 0 and randsc <= 50:
        return 0  # Public
    elif randsc > 50 and randsc <= 100:
        return 1  # Classified

def topo_map():
    executions=100
    avg_solution = {}
    avg_misses = {}
    infcounter=0
    for round in range(0,executions):
        graph, cap_graph, max_rule_graph, nodes, arcs = getGraph()

        node_neighbors={}
        for (i,j) in arcs:
            if not node_neighbors.has_key(i):
                node_neighbors[i] = []
            node_neighbors[i].append(j)

        edge_nodes=[]
        for i in node_neighbors.keys():
            if len(node_neighbors[i]) == 1:
                edge_nodes.append(i)

        print edge_nodes

        security_labels = {}

        for i in nodes:
            security_labels[i] = {}
            security_labels[i][0] = get_rand_secclass()
            for c in range(1,6):
                security_labels[i][c] = get_rand_seccategory()

        #secure_path(nodes,arcs,cap_graph,security_labels)
        #secure_path_sumvio(nodes, arcs, cap_graph, security_labels)
        solution,missingcats = secure_path_minviobound(nodes, arcs, cap_graph, security_labels)
        if solution != 'Infeasible':
            avg_solution[round] = solution
            avg_misses[round] = missingcats
        else:
            infcounter+=1

    avgresults={}
    for rkey in avg_solution.keys():
        for key in avg_solution[rkey]:
            for (i,j,seci,secj) in avg_solution[rkey][key]:
                if not avgresults.has_key(key):
                    avgresults[key] = []
                avgresults[key].append((i,j,seci,secj))
    visualize_results(avgresults,executions)

    avgresults={}
    for rkey in avg_misses.keys():
        for key in avg_misses[rkey]:
            cnt = avg_misses[rkey][key]
            if not avgresults.has_key(key):
                avgresults[key] = 0
            avgresults[key] = avgresults[key] + cnt
    visualize_misses(avgresults,executions)

    print 'Infeasible counter: ' + str(infcounter)
    return security_labels
topo_map()