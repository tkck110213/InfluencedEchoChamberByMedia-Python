from model import agent
from model import social_media
from model.const  import Const
from tqdm import tqdm
import random
import numpy as np
from model import export as ex
import datetime


class EchoChamber:
    def __init__(self, const):
        self.const = const
        self.sns = social_media.SNS(self.const)
        self.agents = [agent.User_Agent(user_num, self.const, self.sns) for user_num in range(self.const.N_user)]
        self.media = [agent.Media_Agent(media_num, self.sns, opinion_range) for media_num, opinion_range in zip(range(self.const.N_user, self.const.N), self.const.opinion_ranges)]

    def dynamics(self, n, root_path):
        """
        関数説明：
        エコーチェンバーモデルの本体
        """
        #各ステップにおける全エージェントのスクリーン上の多様性の平均
        agents_mean_diversity = []

        for t in range(self.const.T):
            #時間tにおける全エージェントのスクリーン多様性を格納
            agents_diversity = [agent.diversity for agent in self.agents]
            #時間tにおける全エージェントのスクリーン多様性の平均を格納
            agents_mean_diversity.append(np.mean(agents_diversity))

            if t % 2000 == 0:
                save_graph_path = root_path + "graph/{}_{}_c{}_mf{}_{}step.gexf".format(n, self.const.follow_method, self.const.confidence, self.const.media_follower, t)
                ex.save_graph(n, t, self.const, self.agents, self.media, self.sns, save_graph_path)

            #行動をするユーザを1人ずつ選ぶ
            user_num = self.user_choice()
            self.agents[user_num].influence()
            self.agents[user_num].post()
            self.agents[user_num].refollow()

            #行動をするメディアを1人ずつ選ぶ
            media_num = self.media_choice()
            self.media[media_num].post()

            #全エージェントの多様性とopinion_historyを更新
            for agent in self.agents:
                agent.renew_diversity_history()

        #時間T(最終ステップ)の全エージェントのスクリーン多様性の平均を格納
        agents_diversity = [agent.diversity for agent in self.agents]
        agents_mean_diversity.append(np.mean(agents_diversity))
        #時間T(最終ステップ)のグラフを出力
        save_graph_path = root_path + "graph/{}_{}_c{}_mf{}_{}step.gexf".format(n, self.const.follow_method, self.const.confidence, self.const.media_follower, self.const.T)
        ex.save_graph(n, self.const.T, self.const, self.agents, self.media, self.sns, save_graph_path)

        #全エージェントの最終ステップまでの意見変化
        agents_alltime_opinions = [agent.opinion_history for agent in self.agents]

        return agents_mean_diversity, agents_alltime_opinions

    def user_choice(self):
        return random.randrange(self.const.N_user)

    def media_choice(self):
        return random.randrange(self.const.N_media)
    


def experiment(follow_method, opinion_ranges, confidence, media_follower):
    const = Const(follow_method, opinion_ranges, confidence, media_follower)
    all_agents_mean_diversity = []
    random.seed(124)
    

    date = datetime.datetime.now()
    root_path = "./result/{}/".format(date.strftime('%Y;%m;%d-%H;%M'))

    for n in tqdm(range(const.max_n)):
        ec = EchoChamber(const)

        #毎試行終了時に、最終ステップまでの多様性平均値と全エージェントの意見データが返される
        agents_mean_diversity, agents_alltime_opinions = ec.dynamics(n, root_path)

        #アンサンプル平均を取るために、各試行の多様性平均値が格納されたニ次元配列を作る
        all_agents_mean_diversity.append(agents_mean_diversity)

        save_opinions_path = root_path + "data/{}_{}_c{}_mf{}_alltime_opinions.csv".format(n, const.follow_method, const.confidence, const.media_follower)
        ex.save_csv(agents_alltime_opinions, save_opinions_path)

    #各ステップにおけるスクリーン上の多様性のアンサンプル平均を取って、csvに出力
    all_agents_mean_diversity = np.array(all_agents_mean_diversity)
    save_csv_path = root_path + "data/{}_{}_c{}_mf{}_amean_diversity.csv".format(n, const.follow_method, const.confidence, const.media_follower)
    ex.save_csv(np.mean(all_agents_mean_diversity, axis=0), save_csv_path)


    

    
    