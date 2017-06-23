import numpy as np
import copy
from PIL.ImageColor import colormap

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from random import shuffle
import os
import scipy as sp
from scipy.interpolate import interp1d
import matplotlib as mpl
import matplotlib
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import operator

def getLine(key):
    lines = {}
    lines[0] = '*'
    lines[1] = '-'
    lines[2] = 'dashed'
    lines[3] = '-.'
    lines[4] = 'dotted'

    return lines[key]

def getLabelViolations(key):
    labels={}
    labels[0] = "None"
    labels[1] = "1 Level"
    labels[2] = "2 Levels"
    labels[3] = "3 Levels"
    labels[4] = "4 Levels"
    return labels[key]

def getLabel(key):
    labels={}
    labels[0] = "N"
    labels[1] = "P"
    labels[2] = "C"
    labels[3] = "S"
    labels[4] = "T"
    return labels[key]

def getLineMarkers(key):
    markers = []
    for m in Line2D.markers:
        try:
            if len(m) == 1 and m != ' ':
                markers.append(m)
        except TypeError:
            pass

    styles = markers + [
        r'$\lambda$',
        r'$\bowtie$',
        r'$\circlearrowleft$',
        r'$\clubsuit$',
        r'$\checkmark$']

    return styles[key]

def getColor(key):
    cmap = matplotlib.cm.get_cmap('jet')
    colors={}
    colors[0] = cmap(0.00)
    colors[1] = cmap(0.25)
    colors[2] = cmap(0.50)
    colors[3] = cmap(0.75)
    colors[4] = cmap(1.00)
    return colors[key]

def getHatches(key):
    hatches={}
    hatches[0] = '+'
    hatches[1] = '.'
    hatches[2] = 'o'
    hatches[3] = '*'
    hatches[4] = '//'
    return hatches[key]

def sumviolations(violations):

    # Have a look at the colormaps here and decide which one you'd like:
    # http://matplotlib.org/1.2.1/examples/pylab_examples/show_colormaps.html

    fig, ax1 = plt.subplots()
    cmap = mpl.cm.summer
    cnt=1
    max=0
    for key in violations.keys():
        col = cmap(1. * cnt / len(violations.keys()))
        #width = 0.2
        y=violations[key]
        x=key
        if max<y:
            max=y
        ax1.bar(x, y, label=str(getLabelViolations(key)), alpha=1, color=getColor(key))
        cnt+1

    ax1.set_ylim((0, (max + 2)))
    ax1.set_xlabel("Security level changes")
    ax1.set_ylabel("Number")

    ax1.legend()
    plt.show()

def stepviolations(violations):

    # Have a look at the colormaps here and decide which one you'd like:
    # http://matplotlib.org/1.2.1/examples/pylab_examples/show_colormaps.html

    fig, ax1 = plt.subplots()
    cmap = matplotlib.cm.get_cmap('jet')
    cnt=1

    for key in violations.keys():
        cweight = 1. * cnt / len(violations.keys())
        col = cmap(cweight)
        #width = 0.2
        y=violations[key]
        width = 0.1
        ax1.bar(cnt, y, label=key, alpha=1, color=col)
        cnt+=1

    rects = ax1.patches

    # Now make some labels
    labels = ["label%d" % i for i in xrange(len(rects))]

    for rect, label in zip(rects, labels):
        height = rect.get_height()
        ax1.text(rect.get_x() + rect.get_width() / 2, height + 5, label, ha='center', va='bottom')

    ax1.set_xlabel("Security level changes")
    ax1.set_ylabel("Number")

    #ax1.legend()
    plt.show()

def categoryvios(violations,model,title):
    cmap = matplotlib.cm.get_cmap('jet')
    width = 0.35  # the width of the bars

    sorted_vio = sorted(violations.items(), key=operator.itemgetter(1))
    for (key,value) in sorted_vio:
        violations[key] = value

    fig, ax = plt.subplots()
    #fig.set_size_inches(24.0, 18.0)
    values=[]
    cnt=1
    xlabels=[]
    max=0
    colors=[]
    #for key in violations.keys():
    for (key,value) in sorted_vio:
        if value>=1:
            values.append(value)
            if max<value:
                max=value
            cweight = 1. * cnt / len(violations.keys())
            xlabels.append(key)
            col = cmap(cweight)
            colors.append(col)
            cnt+=1
    ind = np.arange(len(values))  # the x locations for the groups

    rects1 = ax.bar(ind, values, width, color=colors)

    ax.set_ylim((0, (max + 10)))
    # add some text for labels, title and axes ticks
    ax.set_title(title)
    ax.set_xticks(ind + width / 2)
    ax.set_ylabel("%")
    #ax.set_xticklabels(range(0,len(violations.keys())))
    ax.set_xticklabels(xlabels, fontsize=10)

    #ax.legend((rects1[0]), ('Men','Woman'))

    ax.set

    def autolabel(rects,labels):
        """
        Attach a text label above each bar displaying its height
        """
        ind=0
        for rect in rects:
            height = rect.get_height()
            #ax.text(rect.get_x() + rect.get_width() / 2., 1.05 * height,'%d' % int(height),ha='center', va='bottom')
            ax.text(rect.get_x() + rect.get_width() / 2., 1.02 * height, '%s' % labels[ind], ha='center', va='bottom', fontsize=10)
            ind+=1

    autolabel(rects1,xlabels)

    plt.savefig('/home/stefan/Dropbox/SDN_Security_Policy/images/' + str(model) + '.png', format='png', dpi=300, bbox_inches='tight')
    plt.show()

def visualize_results(solution,executions):

    violations={}
    transitions = 0
    for h in solution.keys():
        for i,j,si,sj in solution[h]:
            transitions += 1
            if si[0]!=0 and sj[0]!=0:
                diff=getLabelViolations(abs(si[0]-sj[0]))
            else:
                diff=getLabelViolations(0)
            if not violations.has_key(diff):
                violations[diff] = 0
            violations[diff] = violations[diff] + 1

    transitions = transitions / executions

    #calc averaage
    for key in violations.keys():
        violations[key] = float(violations[key]) / float(executions)
        violations[key] = (float(violations[key]) / float(transitions))*100

    #sumviolations(violations)
    categoryvios(violations,'static_sumviolations','Security violations')

    secchanges={}
    transitions = 0
    for h in solution.keys():
        for i,j,si,sj in solution[h]:
            transitions += 1
            key = getLabel(si[0]) + ">" + getLabel(sj[0])
            if not secchanges.has_key(key):
                secchanges[key]=0
            secchanges[key]=secchanges[key]+1

    transitions = transitions / executions

    # calc averaage
    for key in secchanges.keys():
        secchanges[key] = float(secchanges[key]) / float(executions)
        secchanges[key] = (float(secchanges[key]) / float(transitions))*100

    #stepviolations(secchanges)
    categoryvios(secchanges,'static_categoryviolations','Security violations')

def visualize_misses(solution,executions):

    misses={}
    sum=0
    for key in solution.keys():
        sum+=solution[key]
    sum = sum / executions

    for key in solution.keys():
        cnt = float(solution[key]) / float(executions)
        cnt = (float(cnt) / float(sum))*100
        misses[str(key) + ' Categories'] = cnt

    #sumviolations(violations)
    categoryvios(misses,'static_catmisses','Missing categories')