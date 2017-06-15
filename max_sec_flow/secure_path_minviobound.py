__author__ = 'stefan'

#!/usr/bin/python

# Copyright 2016, Gurobi Optimization, Inc.

# Solve a multi-commodity flow problem.  Two products ('Pencils' and 'Pens')
# are produced in 2 cities ('Detroit' and 'Denver') and must be sent to
# warehouses in 3 cities ('Boston', 'New York', and 'Seattle') to
# satisfy demand ('inflow[h,i]').
#
# Flows on the transportation network must respect arc capacity constraints
# ('capacity[i,j]'). The objective is to minimize the sum of the arc
# transportation costs ('cost[i,j]').

from gurobipy import *
import random
import copy
from draw_graph import draw_graph
from result_evaluation import visualize_results

def secure_path_minviobound(nodes,arcs,capacity,security_labels):

    commodities=[]

    production={}
    demand={}
    fd={}

    sec_classes=security_labels
    sec_categories={}

    arc_nodes={}
    for i in nodes:
        arc_nodes[i]=[]
        for j in nodes:
            if (i,j) in arcs:
                arc_nodes[i].append(j)

    for c in range(0,10):
        commodities.append('c' + str(c))

    sources = {}
    sourcenodes = {}
    targets = {}
    for i in range(0, 10):
        s_node = random.choice(nodes)
        while s_node in sources.items():
            s_node = random.choice(nodes)
        sources[i] = (s_node)

        c = commodities[i]
        production[c,s_node]=5
        sourcenodes[c] = s_node
        fd[c]=5

    for i in range(0, 35):
        t_node = random.choice(nodes)
        while t_node in sources.items() and t_node in targets.items():
            t_node = random.choice(nodes)
        targets[i] = (t_node)
        #c = commodities[i]
        #demand[c, t_node] = 1

        for c in commodities:
            demand[c, t_node] = 1

    gamma = 100

    # RUN OPTIMIZATION MODEL
    # Create optimization model
    m = Model('securepaths')

    flow = {}
    for h in commodities:
        for i,j in arcs:
            flow[h,i,j] = m.addVar(vtype=GRB.BINARY, name='flow_%s_%s_%s' % (h,i,j)) #, obj=cost[h,i,j]

    delta = {}
    for h in commodities:
        for t in targets.values():
            delta[t,h] = m.addVar(vtype=GRB.BINARY, name='delta_%s_%s' % (t, h))  # , obj=cost[h,i,j]


    #+ 1000*quicksum((sec_classes[sourcenodes[h]][c] + sec_classes[j][c])%2 for c in range(1,6))
    m.update()
    m.setObjective(quicksum(quicksum(flow[h, i, j] * (pow(gamma,abs(sec_classes[sourcenodes[h]][0] - sec_classes[j][0]))) for i, j in arcs) + pow(gamma,2)*quicksum(quicksum(delta[t,h]*(sec_classes[sourcenodes[h]][c]-sec_classes[sourcenodes[h]][c]*sec_classes[t][c]) for c in range(1,6)) for t in targets.values()) for h in commodities), GRB.MINIMIZE)
    #m.setObjective((gamma), GRB.MINIMIZE)
    m.update()

    for i in nodes:
        for h in commodities:
            #m.addConstr(quicksum(z[h,i,j] for j in nodes if (i,j) in arcs) <= 1,'sum_%s_%s_%s' % (i, j, h))
            m.addConstr(quicksum(flow[h,i,j] for j in arc_nodes[i]) <= 1, 'arcflow_%s_%s_%s' % (i, j, h))

    for h in commodities:
        m.addConstr(quicksum(delta[t,h] for t in targets.values()) == 1, 'delta_%s_%s' % (t,h))

    #for h in commodities:
    #    s = sourcenodes[h]
    #    for t in targets.values():
    #        m.addConstr(delta[t, h] * quicksum(sec_classes[s][c]*sec_classes[t][c] for c in range(1,6)) <= delta[t, h] * quicksum(sec_classes[s][c] for c in range(1,6)), 'destcat_%s_%s_%s' % (s,t,h))

    # Arc capacity constraints
    for i,j in arcs:
        m.addConstr(quicksum(flow[h,i,j]*fd[h] for h in commodities) <= capacity[i,j],'cap_%s_%s' % (i, j))

    for h in commodities:
        for j in nodes:
            if (h, j) in production:
                m.addConstr(quicksum(flow[h,i,j] for i,j in arcs.select('*',j)) + 1 == quicksum(flow[h,j,k] for j,k in arcs.select(j,'*')), 'flowconst_%s_%s' % (h, j))
            elif (h, j) in demand:
                m.addConstr(quicksum(flow[h,i,k] for i,k in arcs.select('*',j)) - delta[j,h] == 0, 'flowconst_%s_%s' % (h, j))
            elif (h, j) not in production and (h, j) not in demand:
                m.addConstr(quicksum(flow[h,i,j] for i,j in arcs.select('*',j)) == quicksum(flow[h,j,k] for j,k in arcs.select(j,'*')), 'flowconst_%s_%s' % (h, j))


    # Compute optimal solution
    #m.setParam(GRB.Param.TimeLimit, 60.0)
    m.optimize()

    grapharcs = []
    solution = {}
    if m.status == GRB.Status.OPTIMAL or m.status == GRB.Status.TIME_LIMIT:
        print "Objective Value " + str(m.objVal)
        #print "Alpha " + str(alpha.x)
        #print "Gamma " + str(gamma.x)
        for h in commodities:
            #print "\n Flow:" + str(h) + "\n"
            for i,j in arcs:
                if flow[h, i, j].x > 0:
                    #print i,'_',sec_classes[i], '->', j,'_',sec_classes[j], ':', str(int(flow[h, i, j].x))
                    grapharcs.append((i, j))
                    if not solution.has_key(h):
                        solution[h] = []
                    solution[h].append((i,j,sec_classes[i],sec_classes[j]))

        #grapharcs=[]
        #for (i,j) in arcs:
        #    grapharcs.append((i,j))

        for h in commodities:
            print "Flow " + str(h)
            if solution.has_key(h):
                for i,j,seci,secj in solution[h]:
                    print i, '_', sec_classes[i][0], '->', j, '_', sec_classes[j][0]

        missingcats={}
        for h in commodities:
            s = sourcenodes[h]
            for t in targets.values():
                if delta[t, h].x > 0:
                    print 'Flow ', h, ' from ', s, ' --> ', t
                    print '{',sec_classes[s][1],sec_classes[s][2],sec_classes[s][3],sec_classes[s][4],sec_classes[s][5],' | ',sec_classes[t][1],sec_classes[t][2],sec_classes[t][3],sec_classes[t][4],sec_classes[t][5], '}', '\n'

                    cnt = 0
                    for c in range(1,6):
                        if sec_classes[s][c]==1 and sec_classes[t][c]==0:
                            cnt+=1
                    if not missingcats.has_key(cnt):
                        missingcats[cnt] = 0
                    missingcats[cnt] = missingcats[cnt] + 1

        #draw_graph(solution)
        #visualize_results(solution)

        print'Done'
        return solution,missingcats
    else:
        #m.computeIIS()
        #m.write("model.ilp");
        return 'Infeasible'

