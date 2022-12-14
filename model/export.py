import os
import matplotlib.pyplot as plt
import networkx as nx
import csv
import numpy as np

def save_graph(n, t, const, agents, media, sns, save_graph_path):

    os.makedirs(os.path.dirname(save_graph_path), exist_ok=True)
    
    for i in range(const.N_user):
        #print(i)
        sns.G.nodes[i]['color'] = agents[i].o
        
    for i, media_num in enumerate(range(const.N_user, const.N)):
        sns.G.nodes[media_num]["color"] = media[i].o

    nx.write_gexf(sns.G, save_graph_path)


def save_csv(data, save_csv_path):
    
    os.makedirs(os.path.dirname(save_csv_path), exist_ok=True)

    with open(save_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        if isinstance(data[0], list):
            writer.writerows(data)
        else:
            writer.writerow(data)

    
def final_export(diversityes, n, prohibit=[]):
    agents_opinions = [agents[i].opinion_data for i in range(len(agents)) if i not in prohibit]
    save_csv(agents_opinions, path + "/{}_finally_opinions.csv".format(n))
    plot_data(agents_opinions, "opinions_{}.svg", n)
    plot_data([np.mean(d) for d in diversityes], "diversityes_{}.svg", n)
    
    for i in range(len(agents)):
        if i not in prohibit:
            agents[i].opinion_data.clear()
        

def plot_data(data, fname, n):
    x_range = [i for i in range(const.T)]
    save_path = path + "/figure/" + fname.format(n)

    if isinstance(data[0], list):
        for i in range(const.N_user):
            plt.plot(x_range, data[i])
    else:
        plt.plot(x_range, data)

    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 10  # 適当に必要なサイズに
    plt.rcParams['xtick.direction'] = 'out'  # in or out
    plt.rcParams['ytick.direction'] = 'out'
    plt.rcParams['axes.xmargin'] = 0.01
    plt.rcParams['axes.ymargin'] = 0.01
    plt.rcParams["legend.fancybox"] = False  # 丸角OFF
    plt.rcParams["legend.framealpha"] = 1  # 透明度の指定、0で塗りつぶしなし
    
    plt.rcParams["legend.edgecolor"] = 'black'  # edgeの色を変更
    plt.xlabel("step")
    plt.ylabel("opinions")

    plt.savefig(save_path)
    plt.clf()
    #plt.show()


def export_const(const, path):
    save_path = path + "/parameter.txt"
    const_txt = """
    N = {}
    E = {}
    EP = {}
    p = {}
    q = {}
    M = {}
    l = {}
    max_n = {}
    origin_seed = {}
    N_media = {}
    N_user = {}
    media_indeg = {}
    media_range = {}
    confidence_media = {}
    T = {}
    method = {}
    unfollow_method = {}
    """.format(const.N, const.E, const.EP, const.p, const.q, const.M, const.l, const.max_n, const.origin_seed, const.N_media, const.N_user, const.media_indeg, const.media_range, const.confidence_media,  const.T, const.method, const.unfollow_type)

    with open(save_path, mode="w") as f:
        f.write(const_txt)
