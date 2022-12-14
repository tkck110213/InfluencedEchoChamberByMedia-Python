class Const:
    def __init__(self, follow_method, opinion_ranges, confidence, media_follower):
        self.N_media = 6
        self.N_user = 100
        self.N = self.N_user + self.N_media
        self.E = 400
        self.EP = 0.4
        self.p = 0.5
        self.q = 0.5
        self.M = 0.5
        self.l = 10
        self.max_n = 10
        self.T = 20000

        self.opinion_ranges = opinion_ranges
        
        self.media_follower = media_follower
        #self.o_range = opinion_range
        self.confidence = confidence
        self.follow_method = follow_method
        #self.unfollow_method = unfollow_type

        
        