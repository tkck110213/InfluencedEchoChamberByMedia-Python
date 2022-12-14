import numpy as np
import random
import statistics as st
import analytics as al


class User_Agent:
    def __init__(self, mynum, const, sns):
        self.sns = sns
        self.const = const
        self.o = random.uniform(-1.0, 1.0)
        self.latest_post = {}
        self.mynum = mynum
        self.opinion_history = [self.o]
        #フォロワーとスクリーンを取得
        self.follows_user, self.follows_media = self.sns.get_follows(self.mynum)
        self.screen_msgs = self.sns.pop(self.follows_user + self.follows_media)
        self.diversity = al.screen_diversity(self.screen_msgs, bins=10)

        if mynum < int(const.N_user * const.confidence):
            self.confidence = True
        else:
            self.confidence = False


    def influence(self):
        """
        関数説明：
        スクリーン上の投稿から影響を受ける
        (1) スクリーン上の一般ユーザの意見を、自分の意見から近いか遠いかで分類
        (2) スクリーン上のメディアの意見を、信頼に基づいて分類
        (3) 自分に近い意見から影響を受ける
        """

        #フォロワーとスクリーンを取得
        self.follows_user, self.follows_media = self.sns.get_follows(self.mynum)
        self.screen_msgs = self.sns.pop(self.follows_user + self.follows_media)

        #スクリーン上に何もないときは、空リストを返す
        if self.screen_msgs == []:
            self.similar = []
            self.notsimi = []

        elif self.screen_msgs != []:
            """(1)の処理"""
            self.similar = [msg for msg in self.screen_msgs if np.abs(self.o - msg["opinion"]) < self.const.EP and msg["post_user"] in self.follows_user]
            self.notsimi = [msg for msg in self.screen_msgs if np.abs(self.o - msg["opinion"]) >= self.const.EP and msg["post_user"] in self.follows_user]

            """(2)の処理"""
            if self.confidence == True:
                #メディアの意見は無条件に影響を受ける
                #メディアのすべての投稿をsimilarに入れる
                #print("influence from media")
                self.similar += [msg for msg in self.screen_msgs if msg["post_user"] in self.follows_media]
                #print(len([msg for msg in self.screen_msgs if msg["post_user"] in follows_media]))  
            else:
                #自分の意見と近いメディアの影響は受ける。
                #近いメディアはsimilarにいれ、遠いメディアはnotsimiに入れる
                self.similar +=  [msg for msg in self.screen_msgs if np.abs(self.o - msg["opinion"]) < self.const.EP  and msg["post_user"] in self.follows_media]
                self.notsimi +=  [msg for msg in self.screen_msgs if np.abs(self.o - msg["opinion"]) >= self.const.EP and msg["post_user"] in self.follows_media]
                #print(len(self.similar))
                           
            """(3)の処理"""
            if len(self.similar) != 0:
                self.o += self.const.M * st.mean([msg["opinion"] - self.o for msg in self.similar])
        
    def post(self): 
        """
        関数説明：
        自分に近い意見・メディアの意見をrepostする。
        もしくは自分の意見をpostする。
        """
        if random.random() < self.const.p:#自分に近い意見かメディアをrepost
            if self.similar != []:#近い意見がないときは何も投稿しない
                repost_msg = random.choice(self.similar)

                #snsのメッセージデータベースに投稿を追加
                self.latest_post = {"post_type":"repost", "post_user":self.mynum, "original_user":repost_msg["original_user"], "opinion":repost_msg["opinion"],  "status":repost_msg["status"]}
                self.sns.push(self.latest_post)
                """
                print("post_user:{}".format(self.mynum))
                print("follower:{}".format(followers))
                print("RT posted:{}".format({"post_user":self.mynum, "origin":repost_msg["origin"], "opinion":repost_msg["opinion"], "status":repost_msg["status"]}))
                """
        else:#自分の意見を投稿
            self.latest_post = {"post_type":"post", "post_user":self.mynum, "original_user":self.mynum, "opinion":self.o, "status":"unread"}
            self.sns.push(self.latest_post)
            """
            print("\npost_user:{}".format(self.mynum))
            print("follower:{}".format(followers))
            print("T posted:{}".format(a))
            """

    def refollow(self):
        """
        関数説明：
        エージェントを1人選んでアンフォローし、新しく1人フォローする
        (1) アンフォロー・フォローするユーザを選択
        (2) アンフォローしたあと、フォローする
        """
        if random.random() < self.const.q:
            """(1)の処理"""
            remove_user, follow_user = self.remove_follow_user_choice()
            #self.diversity = al.screen_diversity([msg["opinion"] for msg in self.sns.pop()], 10)
            
            """(2)の処理"""
            if remove_user != None and follow_user != None:
                self.sns.G.remove_edge(self.mynum, remove_user)                          
                self.sns.G.add_edge(self.mynum, follow_user)
           
            
        """
        print("follows:{}".format(self.sns.get_follows(self.mynum, split=True)))
        print("follows:{}".format(set(self.sns.get_follows(self.mynum, split=False))))
        print("msgs_users:{}".format(set([msg["post_user"]  for msg in self.screen.msgs])))
        """
    
    def remove_follow_user_choice(self):
        """
        関数説明：
        アンフォローするユーザとフォローするユーザを選択し返す
        (1) アンフォローするユーザを選択
        (2) フォローするユーザを選択
        """
        
        """(1)の処理"""
        if self.notsimi != []: #スクリーン内の意見の合わないユーザを一人選ぶ
            remove_candidates = [msg["post_user"] for msg in self.notsimi]
            remove_user = random.choice(remove_candidates)
        else: #意見の合わないユーザがいない場合は何も返さない
            remove_user = None

        """(2の処理)"""
        #フォローしてはいけないユーザのリスト(自分やアンフォローするユーザなど)
        prohibit = [self.mynum, remove_user] + self.follows_user + self.follows_media

        if self.const.follow_method == "repost":
            follow_candidates = [msg["original_user"] for msg in self.screen_msgs if msg["post_type"] == "repost" and msg["original_user"] not in prohibit]

        elif self.const.follow_method == "recommendation":
            follow_candidates = self.sns.recommend_user(self.latest_post, prohibit)

        #methodがrandomのとき、もしくは他の手法で候補者が見つけられなかったとき
        if self.const.follow_method == "random" or follow_candidates == []:
            follow_candidates = [user for user in range(self.const.N) if user not in prohibit]

        follow_user = random.choice(follow_candidates)

        return remove_user, follow_user

    def renew_diversity_history(self):
        self.diversity = al.screen_diversity([msg["opinion"] for msg in self.screen_msgs], bins=10)
        self.opinion_history.append(self.o)


class Media_Agent:
    def __init__(self, mynum, sns, opinion_range):
        self.sns = sns
        self.mynum = mynum
        self.opinion_range = opinion_range   
        self.o = random.uniform(self.opinion_range[0], self.opinion_range[1])        

    def post(self):
        """
        関数説明：
        opinion range内の意見をsnsのメッセージデータベースに投稿する
        """
        self.o = random.uniform(self.opinion_range[0], self.opinion_range[1])
        self.sns.push({"post_type":"post", "post_user":self.mynum, "original_user":self.mynum, "opinion":self.o, "status":"unread"})