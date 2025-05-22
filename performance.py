import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from glob import glob

csv_folder = "Performance_4/data"  # Đổi đường dẫn file dữ liệu nếu cần
csv_files = glob(os.path.join(csv_folder, "*.csv"))


output_folder = "Performance_4/test/test_5" # Đường dẫn thư mục lưu biểu đồ
os.makedirs(output_folder, exist_ok=True)

# Đọc và gộp dữ liệu từ nhiều file
all_dfs = []
for file in csv_files:
    df = pd.read_csv(file, header=None, names=["Move", "Time", "Stage"])
    all_dfs.append(df)

combined_df = pd.concat(all_dfs, ignore_index=True)

# --------- Tính trung bình thời gian theo từng Move và Stage ---------
mean_by_move_stage = combined_df.groupby(["Move", "Stage"], as_index=False)["Time"].mean()

# --------- Biểu đồ 1: Trung bình thời gian từng nước đi theo giai đoạn ---------
plt.figure(figsize=(10, 5))
sns.lineplot(data=mean_by_move_stage, x="Move", y="Time", hue="Stage", marker="o")
plt.title("Thời gian suy nghĩ trung bình của AI theo từng nước đi")
plt.xlabel("Số nước đi của AI")
plt.ylabel("Thời gian trung bình (ms)")
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "avg_timing_by_move_and_stage.png"))
plt.show()

# --------- Biểu đồ 2: Trung bình thời gian theo giai đoạn ---------
plt.figure(figsize=(6, 4))
avg_by_stage = combined_df.groupby("Stage")["Time"].mean().reindex(["Opening", "Middlegame", "Endgame"])
avg_by_stage.plot(kind="bar", color=["green", "orange", "red"])
plt.title("Thời gian trung bình của AI theo giai đoạn")
plt.ylabel("Thời gian trung bình (ms)")
plt.xticks(rotation=0)
plt.grid(axis='y')
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "avg_time_by_stage.png"))
plt.show()