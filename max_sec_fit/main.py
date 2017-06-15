from gurobipy import *
from secure_path import secure_path

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
    fname="/home/stefan/Desktop/FLIP/Rocketfuel/3967/weights.intra"
    #fname = "/home/stefan/Desktop/FLIP/Rocketfuel/1239/weights.intra"

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

def topo_map():
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

    security_labels_sources = {}
    security_labels_destinations = {}
    print calc_sec_category([1,1,0,1,0])
    '''
    security_labels['Austin,+TX136'] = (get_security_class('Public'),calc_sec_category([1,1,0,1,0]))
    security_labels['London277'] = (get_security_class('Secret'),calc_sec_category([1,1,1,1,1]))
    security_labels['Frankfurt185'] = (get_security_class('Public'),calc_sec_category([1,1,1,1,1]))

    security_labels['Irvine,+CA212'] = (get_security_class('Public'),calc_sec_category([1,1,1,1,0]))
    security_labels['Toronto,+Canada537'] = (get_security_class('Public'),calc_sec_category([1,0,0,1,0]))
    security_labels['Toronto,+Canada538'] = (get_security_class('Public'),calc_sec_category([1,0,0,1,1]))
    security_labels['Frankfurt184'] = (get_security_class('Secret'),calc_sec_category([1,0,0,1,1]))
    '''

    security_labels_sources['Austin,+TX136'] = (get_security_class('Public'),[1,1,0,1,0])
    security_labels_sources['London277'] = (get_security_class('Public'),[1,1,1,1,1])
    security_labels_sources['Frankfurt185'] = (get_security_class('Public'),[1,1,1,1,1])

    security_labels_destinations['Irvine,+CA212'] = (get_security_class('Public'),[1,1,1,1,0])
    security_labels_destinations['Toronto,+Canada537'] = (get_security_class('Public'),[1,0,0,1,0])
    security_labels_destinations['Toronto,+Canada538'] = (get_security_class('Public'),[1,0,0,1,1])
    security_labels_destinations['Frankfurt184'] = (get_security_class('Public'),[1,0,0,1,1])


    secure_path(nodes,arcs,cap_graph,security_labels_sources,security_labels_destinations)

    return [security_labels_sources,security_labels_destinations]
topo_map()