import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Đọc dữ liệu
df = pd.read_csv("ai_move_timing_log_depth=4.csv", header=None, names=["Move", "Time", "Stage"])

# --------- Biểu đồ 1: Thời gian từng nước đi kèm giai đoạn ---------
plt.figure(figsize=(10, 5))
sns.lineplot(data=df, x="Move", y="Time", hue="Stage", marker="o")
plt.title("Thời gian suy nghĩ của AI theo từng nước đi")
plt.xlabel("Số nước đi của AI")
plt.ylabel("Thời gian (ms)")
plt.grid(True)
plt.tight_layout()
plt.savefig("ai_timing_by_move_stage.png")
plt.show()

# --------- Biểu đồ 2: Trung bình thời gian theo từng giai đoạn ---------
plt.figure(figsize=(6, 4))
avg_by_stage = df.groupby("Stage")["Time"].mean().reindex(["Opening", "Middlegame", "Endgame"])
avg_by_stage.plot(kind="bar", color=["green", "orange", "red"])
plt.title("Thời gian trung bình của AI theo giai đoạn ván cờ")
plt.ylabel("Thời gian trung bình (ms)")
plt.xticks(rotation=0)
plt.grid(axis='y')
plt.tight_layout()
plt.savefig("ai_avg_time_by_stage.png")
plt.show()