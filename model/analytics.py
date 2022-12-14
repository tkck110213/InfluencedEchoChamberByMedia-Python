from typing import Sequence
import networkx as nx
import numpy as np
import scipy.stats as stats

def closed_cluster(G, agents, const):
    num_closed_cluster = 0
    num_dis = 0


    for C in [G.subgraph(c) for c in nx.weakly_connected_components(G)]:
        _agents = [agents[i] for i in list(C.nodes())]
        opinions = [agent.o for agent in _agents]
        diff_o = np.abs(max(opinions) - min(opinions))
        
        if diff_o < const.EP:
            num_dis += 1

    return len([G.subgraph(c) for c in nx.weakly_connected_components(G)])

def screen_diversity(content_values, bins):
    h, w = np.histogram(content_values, range=(-1, 1), bins=bins)
    return stats.entropy(h+1, base=2)





