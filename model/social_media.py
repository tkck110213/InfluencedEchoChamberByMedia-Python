import networkx as nx
import random

class SNS:
    def __init__(self, const):
       self.const = const
       self.G = self.make_graph()
       self.msg_db = []

    def make_graph(self):
        """
        関数説明：
        ソーシャルネットワークの作成
        (1) 一般ユーザのみでランダムグラフを作成
        (2) 出次数が0のユーザをノードに接続する。
            総辺数を変えないために、出次数が2以上のノードを一つ選び、
        　　そのノードの一つの辺を削除して、出次数0のノードと接続する
        (3) 一般ユーザのみのネットワークにメディアを追加する。
        　　ランダムにmedia_follower人のユーザを選び、メディアと接続する
        """

        """(1)の処理"""
        G = nx.gnm_random_graph(self.const.N_user, self.const.E, directed=True)

        """(2)の処理"""
        targets = []
        noouts = []
        for n, out in list(G.out_degree()):
            if out >= 2:
                targets.append(n)
            elif out == 0:
                noouts.append(n)

        for noout in noouts:
            target_agent = random.choice(targets)
            target_edge = random.choice(list(G.edges(target_agent)))
            
            G.remove_edge(target_edge[0], target_edge[1])
            G.add_edge(noout, target_edge[1])

        """(3)の処理"""
        media = [medium for medium in range(self.const.N_user, self.const.N)]   
        users = [user for user in range(self.const.N_user)]
        all_followers = [random.sample(users, self.const.media_follower) for j in range(self.const.N_media)]
        G.add_nodes_from(media)

        #ノードのラベルの設定
        for i in range(self.const.N_user):
            if i < int(self.const.N_user * self.const.confidence):
                G.nodes[i]["label"] = "c"
            else:
                G.nodes[i]["label"] = ""               

        for i in range(self.const.N_user, self.const.N):
            G.nodes[i]["label"] = "media"
        
        #メディアとフォロワーたちを接続する
        for medium, followers in zip(media, all_followers):
            G.add_edges_from([(follower, medium) for follower in followers]) 

        return G        

    def get_follows(self, user_num, split = True):
        """
        関数説明：
        指定したユーザのフォロー取得関数
        """
        follows = list(self.G.neighbors(user_num))

        if split == True:
            follows_media = [f for f in follows if f >= self.const.N_user]
            follows_user = list(set(follows) - set(follows_media))
            return follows_user, follows_media
        else:
            return follows
    
    def get_followers(self, user_num):
        """
        関数説明：
        指定したユーザのフォロワー取得関数
        """
        return list(self.G.predecessors(user_num))

    def push(self, msg):
        """
        関数説明：
        DBの先頭に要素を追加
        """
        #データベースの先頭に最新の投稿を収納
        self.msg_db.insert(0, msg)

    def recommend_user(self, latest_post, prohibit):
        """
        関数説明：
        与えられたユーザに近い別のユーザを返す
        """
        
        recommendtion_users = []

        for msg in self.msg_db:
            if abs(msg["opinion"] - latest_post["opinion"]) < self.const.EP:
                recommendtion_users.append(msg["post_user"])

            if len(recommendtion_users) >= self.const.N:
                break

        if len(recommendtion_users) > 0:
            recommendtion_users = list(set([user for user in recommendtion_users if user not in prohibit]))
            
        return recommendtion_users

    def pop(self, follows):
        """
        関数説明：
        スクリーン(最新l個のフォローユーザの投稿)を返す
        """
        screen = []
        for msg in self.msg_db:
            if msg["post_user"] in follows:
                screen.append(msg)
            if len(screen) >= self.const.l:
                break

        return screen
        