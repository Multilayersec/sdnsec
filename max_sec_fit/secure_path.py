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

def secure_path(nodes,arcs,capacity,security_labels_sources,security_labels_destinations):

    commodities=[]
    dh={}

    production={}
    demand={}

    sec_classes={}
    sec_categories={}

    arc_nodes={}
    for i in nodes:
        arc_nodes[i]=[]
        for j in nodes:
            if (i,j) in arcs:
                arc_nodes[i].append(j)

    production['c1', 'Austin,+TX136'] = 1
    production['c2', 'London277'] = 1
    production['c3', 'Frankfurt185'] = 1
    dh['c1'] = 1
    dh['c2'] = 1
    dh['c3'] = 1
    commodities.append('c1')
    commodities.append('c2')
    commodities.append('c3')

    #demand['c1', 'Irvine,+CA212'] = 1
    #demand['c2', 'Toronto,+Canada537'] = 1
    #demand['c3', 'Frankfurt184'] = 1


    for i in range(1,4):
        demand['c'+str(i), 'Irvine,+CA212'] = 1
        demand['c'+str(i), 'Toronto,+Canada537'] = 1
        demand['c'+str(i), 'Toronto,+Canada538'] = 1
        demand['c'+str(i), 'Frankfurt184'] = 1


    for key in security_labels_destinations:
        (seccl,secca) = security_labels_destinations[key]
        sec_classes[key] = seccl
        sec_categories[key] = secca

    for key in security_labels_sources:
        (seccl,secca) = security_labels_sources[key]
        sec_classes[key] = seccl

    sec_source_cat={}
    (temp, sec_source_cat['c1']) = security_labels_sources['Austin,+TX136']
    (temp, sec_source_cat['c2']) = security_labels_sources['London277']
    (temp, sec_source_cat['c3']) = security_labels_sources['Frankfurt185']

    for i in nodes:
        if not sec_categories.has_key(i):
            sec_categories[i] = [0,0,0,0,0]

    '''
    source_links=[]
    destination_links=[]
    for (h,i) in production:
        for (k,j) in arcs:
            if i==k:
                source_links.append((i,j))

    for (h, i) in demand:
        for (k, j) in arcs:
            if i == j:
                destination_links.append((k, i))
    '''

    # RUN OPTIMIZATION MODEL
    # Create optimization model
    m = Model('securepaths')

    z = {}
    for h in commodities:
        for i,j in arcs:
            z[h,i,j] = m.addVar(vtype=GRB.BINARY, name='z_%s_%s_%s' % (h,i,j)) #, obj=cost[h,i,j]

    m.update()
    m.setObjective(quicksum(quicksum(sec_source_cat[h][k]*quicksum(z[h,i,j]*sec_categories[j][k] for (i,j) in arcs) for k in range(0,len(sec_categories[i]))) for h in commodities), GRB.MAXIMIZE)
    m.update()
    #GRBaddgenconstrAnd
    for i in nodes:
        for h in commodities:
            #m.addConstr(quicksum(z[h,i,j] for j in nodes if (i,j) in arcs) <= 1,'sum_%s_%s_%s' % (i, j, h))
            m.addConstr(quicksum(z[h, i, j] for j in arc_nodes[i]) <= 1, 'arcflow_%s_%s_%s' % (i, j, h))
    '''
    for h in commodities:
        for fs,s in production.keys():
            for j in arc_nodes[s]:
                for ft,t in demand.keys():
                    for i in arc_nodes[t]:
    '''
    for h in commodities:
        for fs, s in production.keys():
            for ft, t in demand.keys():
                m.addConstr((z[h, s, j]*sec_classes[s] for i,j in arcs.select(s,'*')) == (z[h, k, t]*sec_classes[t] for k,l in arcs.select('*',t)), 'secclass_%s_%s_%s' % (s, t, h))

    '''
    for h in commodities:
        for j in nodes:
            if (h, j) in production:
                m.addConstr(quicksum(z[h, i, j] for i, j in arcs.select('*', j)) + sec_classes[s] == quicksum(z[h, j, k] for j, k in arcs.select(j, '*')), 'node_%s_%s' % (h, j))
            elif (h, j) in demand:
                m.addConstr(quicksum(z[h, i, k] - z[h, i, k] * demand[h, j] / dh[h] for i, k in arcs.select('*', j)) == quicksum(z[h, j, k] for j, k in arcs.select(j, '*')), 'node_%s_%s' % (h, j))
            elif (h, j) not in production and (h, j) not in demand:
                m.addConstr(quicksum(z[h, i, j] for i, j in arcs.select('*', j)) == quicksum(z[h, j, k] for j, k in arcs.select(j, '*')), 'node_%s_%s' % (h, j))
    '''

    # Arc capacity constraints
    for i,j in arcs:
        m.addConstr(quicksum(z[h,i,j]*dh[h] for h in commodities) <= capacity[i,j],'cap_%s_%s' % (i, j))

    for h in commodities:
        for j in nodes:
            if (h, j) in production:
                m.addConstr(quicksum(z[h,i,j] for i,j in arcs.select('*',j)) + production[h,j]/dh[h] == quicksum(z[h,j,k] for j,k in arcs.select(j,'*')), 'node_%s_%s' % (h, j))
            elif (h, j) in demand:
                m.addConstr(quicksum(z[h,i,k] - z[h,i,k]*demand[h,j]/dh[h] for i,k in arcs.select('*',j)) == quicksum(z[h,j,k] for j,k in arcs.select(j,'*')), 'node_%s_%s' % (h, j))
            elif (h, j) not in production and (h, j) not in demand:
                m.addConstr(quicksum(z[h,i,j] for i,j in arcs.select('*',j)) == quicksum(z[h,j,k] for j,k in arcs.select(j,'*')), 'node_%s_%s' % (h, j))


    # Compute optimal solution
    #m.setParam(GRB.Param.TimeLimit, 60.0)
    m.optimize()

    if m.status == GRB.Status.OPTIMAL or m.status == GRB.Status.TIME_LIMIT:
        print "Objective Value " + str(m.objVal)
        for h in commodities:
            print "\n Flow:" + str(h) + "\n"
            for i,j in arcs:
                if z[h, i, j].x > 0:
                    print i, '->', j, ':', str(int(z[h, i, j].x))
    else:
        m.computeIIS()
        m.write("model.ilp");
