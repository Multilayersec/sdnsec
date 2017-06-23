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

    capac = 100

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
        return 0

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
    rounds=10
    avg_solution = {}
    avg_misses = {}
    infcounter=0

    dynamic = 0

    for round in range(0,executions):
        graph, cap_graph, max_rule_graph, nodes, arcs = getGraph()

        #define pool of source and target nodes with labels
        #*****************************
        sourcepool = []
        targetpool = []


        for i in range(0, 30):
            s_node = random.choice(nodes)
            while s_node in sourcepool:
                s_node = random.choice(nodes)
            sourcepool.append(s_node)

        for i in range(0, 50):
            t_node = random.choice(nodes)
            while t_node in sourcepool or t_node in targetpool:
                t_node = random.choice(nodes)
            targetpool.append(t_node)
            # c = commodities[i]
            # demand[c, t_node] = 1

        security_labels = {}
        for i in nodes:
            security_labels[i] = {}
            if i in sourcepool or i in targetpool:
                security_labels[i][0] = get_rand_secclass()
                for c in range(1,6):
                    security_labels[i][c] = get_rand_seccategory()
            else:
                if dynamic==0:
                    security_labels[i][0] = get_rand_secclass()
                else:
                    security_labels[i][0] = 0
                for c in range(1, 6):
                    security_labels[i][c] = 0
        # *****************************

        print "SEC labels initial.."
        for c in range(0, 5):
            cnt = 0
            for k in security_labels.keys():
                if security_labels[k][0] == c:
                    cnt += 1
            print "Category " + str(c) + " cnt: " + str(cnt)

        commodities = []
        comcounter=0

        fd = {}
        sourcenodes = {}
        production = []
        demand = []

        nodeusage = {}
        for netconf in range(0, rounds):
            round_commodities = {}
            round_commodities_list = []
            sources = {}
            targets = {}

            #add commodities
            for c in range(0, 10):
                commodities.append('c' + str(comcounter))
                fd['c' + str(comcounter)] = 1
                round_commodities[c] = 'c' + str(comcounter)
                round_commodities_list.append('c' + str(comcounter))
                comcounter+=1

            #select random sources and destinations
            for i in range(0, 10):
                s_node = random.choice(sourcepool)
                while s_node in sources.values():
                    s_node = random.choice(sourcepool)
                sources[i] = (s_node)
                sourcenodes[round_commodities[i]] = (s_node)
                production.append((s_node,round_commodities[i]))

            for i in range(0, 25):
                t_node = random.choice(targetpool)
                while t_node in sources.values() or t_node in targets.values():
                    t_node = random.choice(targetpool)
                targets[i] = (t_node)
                for c in round_commodities.values():
                    demand.append((t_node,c))

            solution,missingcats = secure_path_minviobound(round_commodities_list, fd, nodes, sourcenodes, production, sources, demand, targets, arcs, cap_graph, security_labels)

            '''
            print "SEC labels before..."
            for c in range(0, 5):
                cnt = 0
                for k in security_labels.keys():
                    if security_labels[k][0] == c:
                        cnt += 1
                print "Category " + str(c) + " cnt: " + str(cnt)
            '''
            if dynamic == 1:
                for key in solution.keys():
                    secclass=None
                    for i,j,si,sj in solution[key]:
                        if not nodeusage.has_key(i):
                            nodeusage[i]=0
                        nodeusage[i] = nodeusage[i] + 1

                        if i == sourcenodes[key]:
                            secclass = si[0]

                    for i, j, si, sj in solution[key]:
                        if security_labels[i][0]==0:
                            security_labels[i][0] = secclass
                            #print " SEC CLASS UPDATE 1"

            '''
            print "SEC labels after.."
            for c in range(0, 5):
                cnt = 0
                for k in security_labels.keys():
                    if security_labels[k][0] == c:
                        cnt += 1
                print "Category " + str(c) + " cnt: " + str(cnt)
            '''

            if solution != 'Infeasible':
                avg_solution[round,netconf] = solution
                avg_misses[round,netconf] = missingcats

                #depart flows
                if dynamic == 1:
                    departing=[]
                    for i in range(0,3):
                        c = random.choice(commodities)
                        departing.append(c)
                        commodities.remove(c)

                    for (curround,curnetconf) in avg_solution.keys():
                        if curround==round and curnetconf==netconf:
                            for com in avg_solution[(curround,curnetconf)].keys():
                                if com in departing:
                                    for i, j, si, sj in avg_solution[(curround,curnetconf)][com]:
                                        nodeusage[i] = nodeusage[i] - 1
                                        if nodeusage[i]==0 and i not in sourcepool and i not in targetpool:
                                            security_labels[i][0] = 0
                                            #print " SEC CLASS UPDATE 2"

            else:
                infcounter+=1

    sumruns=executions*rounds

    avgresults={}
    for (rkey,confkey) in avg_solution.keys():
        for key in avg_solution[(rkey,confkey)]:
            for (i,j,seci,secj) in avg_solution[(rkey,confkey)][key]:
                if not avgresults.has_key(key):
                    avgresults[key] = []
                avgresults[key].append((i,j,seci,secj))
    visualize_results(avgresults,sumruns)

    avgresults={}
    for (rkey,confkey) in avg_misses.keys():
        for key in avg_misses[(rkey,confkey)]:
            cnt = avg_misses[(rkey,confkey)][key]
            if not avgresults.has_key(key):
                avgresults[key] = 0
            avgresults[key] = avgresults[key] + cnt
    visualize_misses(avgresults,sumruns)

    print 'Infeasible counter: ' + str(infcounter)
    return security_labels
topo_map()