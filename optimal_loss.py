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
from capacity_setting import get_fixed_capacity
from capacity_setting import get_flow_upper_bound
from rule_analyzer import analyze_rules
import copy
from calc_flow_disruption import flow_disruption
from switch_rule_map import create_switch_rule_map
from switch_rule_map import visualize_map
from mcf_min_congestion_BF import minimize_congestion
from loss_calculator import calc_loss

def optimal_loss_model(networktopo,execs,flowam,flowinc,numflows,departing):

    #fname="/home/stefan/Desktop/FLIP/Rocketfuel/1239/weights.intra"
    fname = networktopo
    capac=get_fixed_capacity()

    nodes=[]
    arcs=[]
    capacity={}
    cost={}

    with open(fname) as f:
        content = f.readlines()
        for line in content:
            e = line.split(" ")
            if e[0] not in nodes:
                nodes.append(e[0])
            if e[1] not in nodes:
                nodes.append(e[1])
            arcs.append((e[0],e[1]))
            capacity[(e[0],e[1])]=capac
            cost[(e[0],e[1])]=float(e[2])
    arcs = tuplelist(arcs)

    flow_amount=flowam
    d_inc=flowinc
    sdn_configurations=[]
    demand = {}
    dh = {}
    production = {}
    commodities = []
    k_list = {}
    com_cnt = 0
    flow_amount += d_inc
    result_list=[]
    rule_out_list = []
    rule_map = {}


    for run in range(0,execs):

        flows = numflows
        #flows = 20
        #com_start_ind = com_cnt
        com_start_ind = len(commodities)
        for i in range(0, flows):
            commodities.append('c' + str(com_cnt))
            com_cnt += 1

        #for hi in range(com_start_ind, len(commodities)):
        for hi in range(com_start_ind, (com_start_ind+flows)):
        #for hi in range(0, flows):
            h = commodities[hi]
            snode = random.choice(nodes)
            tnode = random.choice(nodes)
            #if not production.has_key((h, snode)) and not demand.has_key((h, tnode)):
            while(snode == tnode):
                snode = random.choice(nodes)
                tnode = random.choice(nodes)
            d = flow_amount  # random.randint(25,75)
            demand[(h, tnode)] = d
            production[(h, snode)] = d
            dh[h] = d


        # RUN OPTIMIZATION MODEL
        # Create optimization model
        m = Model('mcf')

        z = {}
        for h in commodities:
            for i,j in arcs:
                z[h,i,j] = m.addVar(vtype=GRB.BINARY, name='z_%s_%s_%s' % (h,i,j)) #, obj=cost[h,i,j]

        a = {}
        for h in commodities:
            a[h] = m.addVar(vtype=GRB.BINARY, name='a_%s' % (h)) #, obj=cost[h,i,j]

        m.update()
        m.setObjective(quicksum(a[h]*dh[h] for h in commodities), GRB.MAXIMIZE)
        m.update()

        for i,j in arcs:
            for h in commodities:
                #m.addConstr(quicksum(z[h,i,j] for j in nodes if (i,j) in arcs) <= 1,'sum_%s_%s_%s' % (i, j, h))
                m.addConstr(z[h, i, j] <= 1, 'arcflow_%s_%s_%s' % (i, j, h))

        # Arc capacity constraints
        for i,j in arcs:
            m.addConstr(quicksum(z[h,i,j]*dh[h] for h in commodities) <= capacity[i,j],'cap_%s_%s' % (i, j))

        for h in commodities:
            for j in nodes:
                if (h, j) in production:
                    m.addConstr(quicksum(z[h,i,j] for i,j in arcs.select('*',j)) + a[h]*production[h,j]/dh[h] == quicksum(z[h,j,k] for j,k in arcs.select(j,'*')), 'node_%s_%s' % (h, j))
                elif (h, j) in demand:
                    m.addConstr(quicksum(z[h,i,j] for i,j in arcs.select('*',j)) - a[h]*demand[h,j]/dh[h] == quicksum(z[h,j,k] for j,k in arcs.select(j,'*')), 'node_%s_%s' % (h, j))
                elif (h, j) not in production and (h, j) not in demand:
                    m.addConstr(quicksum(z[h,i,j] for i,j in arcs.select('*',j)) == quicksum(z[h,j,k] for j,k in arcs.select(j,'*')), 'node_%s_%s' % (h, j))


        # Compute optimal solution
        #m.setParam(GRB.Param.TimeLimit, 60.0)
        m.optimize()

        # Print solution
        solution=[]
        rules=[]
        sum_flow = 0
        actual_flow = 0
        sum_rules = 0
        calc_changes = 0
        sum_disruptions = 0
        all_rules = []
        round_commodities = []
        path_solution = {}
        if m.status == GRB.Status.OPTIMAL or m.status == GRB.Status.TIME_LIMIT:
            print "Objective Value " + str(m.objVal)
            for h in commodities:
                sum_flow+=flow_amount
                round_commodities.append(h)
                #print '\nOptimal flows for', h, ':'
                #for k in nodes:
                    #if (h,k) in production:
                        #sum_flow += fraction[(h,k)].x*production[(h,k)]
                for i,j in arcs:
                    if z[h,i,j].x > 0: # and updates[h, i, j].x==1
                        path_solution[(i, j, h)] = flow_amount
                        #print i, '->', j, ':', str(int(z[h, i, j].x)) #*updates[h, i, j].x #, ' frac ', i, ': ', fraction[(h, i)].x, ' frac ', j, ': ', fraction[(h, j)].x
                        sum_rules+=1
                        solution.append((i,j,h))
                        #capacity[i, j] = capacity[i, j] - 30
                        all_rules.append((i, j, z[h, i, j].x, h))
                        rules.append((i, j, z[h, i, j].x, h))
                    k_list[(h, i, j)] = int(z[h,i,j].x)

        aloss=0
        lost_commodities=[]
        for h in commodities:
            if a[h].x==0:
                aloss+=flow_amount
                lost_commodities.append(h)

        loss=(flow_amount*len(commodities)) - int(m.objVal)
        print "Loss " + str(loss) + " ALoss " + str(aloss)

        for lc in lost_commodities:
            commodities.remove(lc)

        sdn_configurations.append(copy.deepcopy(rules))
        #calc_changes+=m.objVal
        print("RUNTIME " + str(m.Runtime))
        if flow_amount>get_flow_upper_bound():
            feasible = 0

        #analyze_rules("unsplittable", rules, arcs, nodes)

        if len(sdn_configurations) > 1:
            config1 = copy.deepcopy(sdn_configurations[0])
            config2 = copy.deepcopy(sdn_configurations[1])

            dis = flow_disruption(copy.deepcopy(config1), copy.deepcopy(config2), commodities)
            sum_disruptions += dis

            for entry in config1:
                if entry in config2:
                    config2.remove(entry)
                #else:
                #    calc_changes += 1
                #only count added rules

            rule_updates = config2
            calc_changes += len(config2)
            sdn_configurations.pop(0)
            print "Rule changes " + str(calc_changes)

        [losscalc, com_loss] = calc_loss(rules, get_fixed_capacity(), flow_amount)
        for c in com_loss:
            if c in commodities:
                commodities.remove(c)

        print "all rules " + str(len(all_rules))
        [output,maxswitch,maxrules] = analyze_rules("Optimalloss", rules, arcs, nodes, flow_amount,run,commodities)
        rule_out_list.append(output)

        result = "Optimalloss," + str(m.Runtime) + "," + str(calc_changes) + "," + str(sum_flow) + "," + str(losscalc) + "," + str(0) + "," + str(sum_disruptions) + "," + str(flow_amount) + "," + str(flows) + "," + str(output) + "," + str(run) + ",0,0,0,0,0,0,0" + "\n"
        result_list.append(result)
        print result

        #REMOVE RANDOM FLOWS
        rf=departing
        for i in range(0,rf):
            randflow = random.choice(commodities)
            commodities.remove(randflow)
            dh.pop(randflow)
            #print "Removed flow " + str(randflow)

        #visualize_map(rule_map,"Optimal")

        #if feasible==1:
        f = open('eval_results.txt', 'a')
        f.write(result)
        f.close()
        feasible = 0
