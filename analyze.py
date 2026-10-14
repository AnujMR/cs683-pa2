import re, glob, os, csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

traces = ["Trace1", "Trace2", "Trace3"]
policies = {
    "LRU": "results/base_%s.txt",
    "RRIP": "results/rrip_%s.txt",
    "I-RRIP": "results/irrip_%s.txt",
    "Dyn I-RRIP (0.25)": "results/dyn_%s.txt",
}

def parse(path):
    if not os.path.exists(path):
        print("MISSING:", path); return None
    txt = open(path).read()
    def g(p):
        m = re.search(p, txt, re.M)
        return float(m.group(1)) if m else None
    d = dict(ipc=g(r"^CPU 0 cumulative IPC: ([\d.]+)"),
             load=g(r"^L2C LOAD +ACCESS.*MPKI: ([\d.]+)"),
             data=g(r"^L2C DATA LOAD MPKI: ([\d.]+)"),
             instr=g(r"^L2C INSTRUCTION LOAD MPKI: ([\d.]+)"),
             total=g(r"^L2C TOTAL +ACCESS.*MPKI: ([\d.]+)"))
    if None in d.values():
        print("INCOMPLETE:", path)
        return None
    return d

R = {p: {t: parse(f % t) for t in traces} for p, f in policies.items()}
os.makedirs("plots", exist_ok=True)

# ---- main table ----
rows = []
for t in traces:
    for p in policies:
        d = R[p][t]
        if d is None: continue
        lru, rrip = R["LRU"][t], R["RRIP"][t]
        s_lru = d["ipc"] / lru["ipc"] if lru else float("nan")
        s_rrip = d["ipc"] / rrip["ipc"] if rrip else float("nan")
        rows.append([t, p, d["ipc"], s_lru, s_rrip, d["total"], d["load"], d["instr"], d["data"]])
hdr = ["trace", "policy", "ipc", "speedup_vs_LRU", "speedup_vs_RRIP",
       "L2C_total_MPKI", "L2C_load_MPKI", "L2_instr_load_MPKI", "L2_data_load_MPKI"]
with open("task2_table.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(hdr); w.writerows(rows)
print(",".join(hdr))
for r in rows:
    print(",".join(r[:2] + ["%.4f" % x for x in r[2:]]))

# ---- bar plots ----
def bars(idx, ylabel, title, fname, pols, hline=None):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    w = 0.8 / len(pols)
    for i, p in enumerate(pols):
        vals = []
        for t in traces:
            m = [r for r in rows if r[0] == t and r[1] == p]
            vals.append(m[0][idx] if m else 0)
        ax.bar([x + i * w for x in range(len(traces))], vals, w, label=p)
    ax.set_xticks([x + w * (len(pols) - 1) / 2 for x in range(len(traces))])
    ax.set_xticklabels(traces)
    ax.set_ylabel(ylabel); ax.set_title(title)
    if hline: ax.axhline(hline, color="red", ls="--", lw=1)
    ax.legend()
    fig.tight_layout(); fig.savefig("plots/" + fname, dpi=150); plt.close(fig)

allp = list(policies)
bars(3, "Speedup over LRU", "Task 2: speedup over LRU", "t2_speedup_lru.png", allp, 1.0)
bars(4, "Speedup over RRIP", "Task 2: speedup over RRIP", "t2_speedup_rrip.png", allp, 1.0)
bars(2, "IPC", "Task 2: IPC", "t2_ipc.png", allp)
bars(6, "L2C load MPKI", "Task 2: L2C load MPKI", "t2_l2c_load_mpki.png", allp)
bars(7, "L2 instruction load MPKI", "Task 2: L2 instruction load MPKI", "t2_instr_mpki.png", allp)
bars(8, "L2 data load MPKI", "Task 2: L2 data load MPKI", "t2_data_mpki.png", allp)

# ---- threshold sweep ----
srows = []
for t in traces:
    for f in glob.glob("results/sweep/dyn_%s_th*.txt" % t):
        th = float(re.search(r"_th([\d.]+)\.txt", f).group(1))
        d = parse(f)
        if d is None: continue
        lru = R["LRU"][t]; rrip = R["RRIP"][t]
        srows.append([t, th, d["ipc"], d["ipc"] / lru["ipc"],
                      d["ipc"] / rrip["ipc"] if rrip else float("nan"),
                      d["load"], d["instr"], d["data"]])
srows.sort()
with open("task2b_sweep.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["trace", "threshold", "ipc", "speedup_vs_LRU", "speedup_vs_RRIP",
                "L2C_load_MPKI", "L2_instr_MPKI", "L2_data_MPKI"])
    w.writerows(srows)
print("\nSWEEP")
for r in srows:
    print(r[0], r[1], ["%.4f" % x for x in r[2:]])

fig, axs = plt.subplots(1, 3, figsize=(15, 4.2))
for k, (idx, lab) in enumerate([(3, "Speedup over LRU"), (5, "L2C load MPKI"), (6, "L2 instr load MPKI")]):
    for t in traces:
        pts = [(r[1], r[idx]) for r in srows if r[0] == t]
        if pts: axs[k].plot(*zip(*pts), marker="o", label=t)
    axs[k].set_xlabel("threshold"); axs[k].set_ylabel(lab); axs[k].legend()
fig.suptitle("Dynamic I-RRIP threshold sensitivity")
fig.tight_layout(); fig.savefig("plots/t2b_sweep.png", dpi=150)
print("\nSaved: task2_table.csv task2b_sweep.csv plots/*.png")
