import matplotlib.pyplot as plt
import os
import constants

contributors = []
with open(os.path.join(os.getcwd(), constants.OUTPUT_DIR, constants.MAIN_TEXT_FILE), 'r') as f:
    lines = f.readlines()
    for line in lines:
        if line in contributors:
            print(line)
            continue
        contributors.append(line.replace('\n', ''))

recency_dict = {
    0: [],
    1: [],
    2: [],
    3: [],
    4: [],
    5: []
}
with open(os.path.join(os.getcwd(), constants.OUTPUT_DIR, constants.RECENCY_CSV), 'r') as f:
    lines = f.readlines()
    for line in lines:
        toks = line.split(',')
        recency_dict[int(toks[1])].append(toks[0])

fig, ax = plt.subplots()
ax.bar(range(len(recency_dict)), [len(value) for value in recency_dict.values()])

for key, val in recency_dict.items():
    ax.text(key-0.175, len(val)+10, f"{len(val)}")
ax.set_xlabel("Years ago")
ax.set_xticks(range(6))
ax.set_xticklabels(["0", "1", "2", "3", "4", "5+"])
ax.set_ylabel("Users")
ax.set_title("Last (public) comment/post among users in r/ravenclaw")
plt.savefig(os.path.join(os.getcwd(), "../output_files/most_recent_post_bars.png"))


for key in recency_dict:
    for val in recency_dict[key]:
        if val == 'chilly-gin-gins':
            print(val)
        contributors.pop(contributors.index(val))
print(contributors)
print(len(contributors))