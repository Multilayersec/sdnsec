from mcf_min_rules_integer_rocketfuel import optimal_model
from greedy_capacity import greedy_capa_model
from greedy_no_capacity import greedy_nocapa_model
from mcf_min_rules_continuous_rocketfuel import randomrounding_model
from mcf_min_rules_non_distruptive_rr import randomrounding_model_nd
from greedy_min_rules_tablesize import greedy_hybrid_model_tablesize
#from result_analyzer import analyze_results
from SelectPaths_greedy import buffered_paths_greedy_model
from SelectPaths_greedy_tablesize import buffered_paths_greedy_model_tablesize
from SelectPaths_optimal_new import buffered_paths_lp_model
from secure_path import optimal_loss_model
from SelectPaths_shortest import buffered_paths_shortest_path
from NewModels.capacity_setting import get_fixed_capacity
from gurobipy import *
import random

def generateGraph(nodes, arcs, h, a):
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
                cap_graph[n][m] = get_fixed_capacity()
        max_rule_graph[n] = init_max_rule

    return graph, cap_graph, max_rule_graph

def getGraph(h,a,topo):

    #Model data
    #fname="/home/stefan/Desktop/FLIP/Rocketfuel/3967/weights.intra"
    #fname = "/home/stefan/Desktop/FLIP/Rocketfuel/1239/weights.intra"
    fname = topo

    capac = get_fixed_capacity()

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

    graph, cap_graph, max_rule_graph = generateGraph(nodes, arcs, h ,a)

    return graph, cap_graph, max_rule_graph, nodes, arcs

#networktopo="/home/stefan/Desktop/FLIP/Rocketfuel/3967/weights.intra"
networktopo="/home/stefan/Desktop/FLIP/Rocketfuel/1239/weights.intra"
execs=20
flowam=1
flowinc=0
numflows=40
k=0.2
departingflows=10

#[1,2,5,10,25]
for x in [25]:
    paths = {}
    sourcepaths = []
    connections = {}
    fname = str(x) + '_paths_1239.txt'
    cnt = 0
    with open(fname) as f:
        content = f.readlines()
        for line in content:
            e = line.split(";")
            cnt += 1
            print "Path " + str(cnt)
            if paths.has_key((e[0], e[len(e) - 2])):
                paths[(e[0], e[len(e) - 2])].append(e)
            else:
                paths[(e[0], e[len(e) - 2])] = []
                paths[(e[0], e[len(e) - 2])].append(e)
            #if e[0] not in sourcepaths:
            #    sourcepaths.append(e[0])
            if not connections.has_key((e[0], e[len(e) - 2])):
                connections[(e[0], e[len(e) - 2])]=1


runs=50

for i in range(0,runs):
    #optimal_model(networktopo, execs, flowam, flowinc, numflows, k, departingflows)
    #optimal_model(networktopo,execs,flowam,flowinc,numflows,k,departingflows)
    #randomrounding_model(networktopo,execs,flowam,flowinc,numflows,k,departingflows)
    #greedy_nocapa_model(networktopo,execs,flowam,flowinc,numflows,departingflows)

    graph, cap_graph, max_rule_graph, nodes, arcs = getGraph(None, None, networktopo)
    sources = {}
    targets = {}
    for round in range(0, execs):
        round_src = {}
        round_dst = {}
        for i in range(0, numflows):
            s_node = random.choice(nodes)
            t_node = random.choice(nodes)
            while s_node == t_node:
                s_node = random.choice(nodes)
                t_node = random.choice(nodes)
            round_src[i] = (s_node)
            round_dst[i] = (t_node)
        sources[round] = round_src
        targets[round] = round_dst

    departing={}
    commos=[]
    c=0
    for round in range(0, execs):
        departinground={}
        for i in range(0, numflows):
            commos.append(c)
            c+=1
        for i in range(0, departingflows):
            com=random.choice(commos)
            departinground[i] = com
            commos.remove(com)
        departing[round] = departinground

    #randomrounding_model_nd(networktopo, execs, flowam, flowinc, numflows, k, departing, sources, targets)
    buffered_paths_lp_model(networktopo, execs, flowam, flowinc, numflows, departing, paths, connections, x, sources, targets)
    greedy_hybrid_model_tablesize(networktopo, execs, flowam, flowinc, numflows, departing, sources, targets)
    buffered_paths_greedy_model_tablesize(networktopo, execs, flowam, flowinc, numflows, departing, paths, connections, x, sources, targets)
    greedy_capa_model(networktopo, execs, flowam, flowinc, numflows, departing, sources, targets)
    buffered_paths_shortest_path(networktopo, execs, flowam, flowinc, numflows, departing, paths, connections, x, sources, targets)

    #buffered_paths_greedy_model(networktopo, execs, flowam, flowinc, numflows, departingflows, paths,connections,x)
    #greedy_hybrid_model(networktopo,execs,flowam,flowinc,numflows,departingflows)
    #optimal_loss_model(networktopo, execs, flowam, flowinc, numflows, departingflows)
