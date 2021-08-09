import matplotlib.pyplot as plt
import os
import constants

"""Like plot_dead_accounts.py but this is specifically for your sub and not reddit as a whole.
    Assuming you have a recency csv (like the one produced by most_recent_ravenclaw_post.py), which looks like...
        User1,0
        User2,0
        User3,1
        User4,3
        User5,2
        User6,1
    i.e. it has a list of members of your subreddit and how many years since they last made a post/comment in your sub, 
    this will save a bar chart showing how many users you have with each timeframe (<1 years, 1, 2, 3, 4, 5+ years since last
    post/comment) in your sub"""


def main():
    recency_dict = {
        0: [],
        1: [],
        2: [],
        3: [],
        4: [],
        5: [],
        -1: []
    }
    with open(os.path.join(os.getcwd(), constants.OUTPUT_DIR, "tower_recency.csv"), 'r') as f:
        lines = f.readlines()
        for line in lines:
            toks = line.split(',')
            recency_dict[int(toks[1])].append(toks[0])
    recency_dict[6] = recency_dict[-1]
    del recency_dict[-1]

    fig, ax = plt.subplots()
    ax.bar(range(len(recency_dict)), [len(value) for value in recency_dict.values()])

    for key, val in recency_dict.items():
        ax.text(key-0.175, len(val)+10, f"{len(val)}")
    ax.set_xlabel("Years ago")
    ax.set_xticks(range(7))
    ax.set_xticklabels(["0", "1", "2", "3", "4", "5+", "Never*"])
    plt.figtext(0.65, 0.01, "*: Within last 1,000 posts/comments", fontsize='small')
    ax.set_ylabel("Users")
    ax.set_title("Last comment/post in r/ravenclaw among \"active\" redditors\n(last reddit post within 1 year)")
    plt.savefig(os.path.join(os.getcwd(), "../output_files/most_recent_tower_post_bars.png"))


if __name__ == '__main__':
    main()
