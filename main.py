from model import echocamber_dynamics

def main():
    refollow_type = "random"
    opinion_ranges = [[-1.0, -0.8], [-0.1, 0.1], [0.8, 1.0], [-1.0, -0.8], [-0.1, 0.1], [0.8, 1.0]]
    confidence_level = 0.6
    media_follower = 15

    echocamber_dynamics.experiment(refollow_type, opinion_ranges, confidence_level, media_follower)

main()