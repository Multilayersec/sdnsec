import networkx as nx
import matplotlib.pyplot as plt

def draw_graph(graph, labels=None, graph_layout='spring',
               node_size=700, node_color='blue', node_alpha=0.15,
               node_text_size=10,
               edge_color='blue', edge_alpha=0.3, edge_tickness=2,
               edge_text_pos=0.3,
               text_font='sans-serif'):

    # create networkx graph
    G=nx.Graph()

    # add edges
    #for edge in graph:
    #    G.add_edge(edge[0], edge[1])
    grapharcs=[]
    labels=[]

    p_edge=[]
    c_edge=[]
    s_edge=[]
    ts_edge=[]
    p_node=[]
    c_node=[]
    s_node=[]
    ts_node=[]
    nodelabels={}

    for flow in graph.keys():
        for (i,j,seci,secj) in graph[flow]:
            ecolor='blue'
            if seci == 1:
                p_edge.append((i,j))
                p_node.append(i)
            if seci == 2:
                c_edge.append((i,j))
                c_node.append(i)
            if seci == 3:
                s_edge.append((i,j))
                s_node.append(i)
            if seci == 4:
                ts_edge.append((i,j))
                ts_node.append(i)
            if secj == 1:
                p_node.append(j)
            if secj == 2:
                c_node.append(j)
            if secj == 3:
                s_node.append(j)
            if secj == 4:
                ts_node.append(j)
            nodelabels[i]=seci
            nodelabels[j]=secj

            G.add_edge(i, j)
            grapharcs.append((i,j))
            #labels.append(str(seci) + "-" + str(secj))
            labels.append(str(flow))

    # these are different layouts for the network you may try
    # shell seems to work best
    if graph_layout == 'spring':
        graph_pos=nx.spring_layout(G)
    elif graph_layout == 'spectral':
        graph_pos=nx.spectral_layout(G)
    elif graph_layout == 'random':
        graph_pos=nx.random_layout(G)
    else:
        graph_pos=nx.shell_layout(G)

    # draw graph
    nx.draw_networkx_nodes(G, graph_pos, nodelist=p_node, node_size=node_size,alpha=node_alpha, node_color='blue')
    nx.draw_networkx_nodes(G, graph_pos, nodelist=c_node, node_size=node_size, alpha=node_alpha, node_color='green')
    nx.draw_networkx_nodes(G, graph_pos, nodelist=s_node, node_size=node_size, alpha=node_alpha, node_color='red')
    nx.draw_networkx_nodes(G, graph_pos, nodelist=ts_node, node_size=node_size, alpha=node_alpha, node_color='black')
    nx.draw_networkx_edges(G, graph_pos, edgelist=p_edge,width=edge_tickness,alpha=edge_alpha,edge_color='blue')
    nx.draw_networkx_edges(G, graph_pos, edgelist=c_edge, width=edge_tickness, alpha=edge_alpha, edge_color='green')
    nx.draw_networkx_edges(G, graph_pos, edgelist=s_edge, width=edge_tickness, alpha=edge_alpha, edge_color='red')
    nx.draw_networkx_edges(G, graph_pos, edgelist=ts_edge, width=edge_tickness, alpha=edge_alpha, edge_color='black')
    nx.draw_networkx_labels(G, graph_pos, labels=nodelabels, font_size=node_text_size,font_family=text_font)

    if labels is None:
        labels = range(len(grapharcs))

    edge_labels = dict(zip(grapharcs, labels))
    nx.draw_networkx_edge_labels(G, graph_pos, edge_labels=edge_labels,
                                 label_pos=edge_text_pos)

    # show graph
    plt.show()