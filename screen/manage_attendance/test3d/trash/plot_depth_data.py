import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Đọc dữ liệu từ file CSV
df = pd.read_csv("trash/depth_data_20250420_152009.csv")

# Đổi tên cột sang tiếng Việt
df.columns = ['nose_depth', 'avg_eye_depth', 'face_std_dev', 'nose_eye_diff', 'label']

# Xử lý giá trị thiếu cho cột nose_eye_diff
df['nose_eye_diff'] = df['nose_eye_diff'].fillna(df['nose_eye_diff'].mean())

# Chuyển nhãn sang tiếng Việt
df['label'] = df['label'].map({'real': 'Thật', 'spoof': 'Giả'})

# Tạo giao diện Tkinter
root = Tk()
root.title("Phân tích chênh lệch mũi-mắt")
root.geometry("800x600")

# Hiển thị thông tin số lượng mẫu
label_counts = df['label'].value_counts()
label_text = (
    f"Số lượng mẫu:\n"
    f" - Thật: {label_counts.get('Thật', 0)} mẫu\n"
    f" - Giả: {label_counts.get('Giả', 0)} mẫu\n"
    f" - Tổng cộng: {len(df)} mẫu"
)
info_label = Label(root, text=label_text, font=("Arial", 12), justify=LEFT, anchor='w')
info_label.pack(pady=10, padx=10, anchor='w')

# Tạo frame chứa biểu đồ
frame = Frame(root)
frame.pack(fill=BOTH, expand=True)

# Vẽ biểu đồ cột
fig, ax = plt.subplots(figsize=(8, 5))
# Vẽ bar plot cho nose_eye_diff
sns.barplot(x='label', y='nose_eye_diff', data=df, ax=ax, palette=['#66c2a5', '#fc8d62'])
ax.set_title('Chênh lệch mũi-mắt theo nhãn', fontsize=14)
ax.set_xlabel('Nhãn', fontsize=12)
ax.set_ylabel('Chênh lệch mũi-mắt (mm)', fontsize=12)
ax.grid(True, axis='y', linestyle='--', alpha=0.7)  # Thêm lưới nền

# Thêm số lượng mẫu và giá trị trung bình
for i, label in enumerate(['Thật', 'Giả']):
    count = label_counts.get(label, 0)
    mean_value = df[df['label'] == label]['nose_eye_diff'].mean() if count > 0 else 0
    # Số lượng mẫu
    ax.text(
        i, mean_value + (ax.get_ylim()[1] * 0.05) if mean_value >= 0 else ax.get_ylim()[1] * 0.95,
        f'n={count}',
        ha='center', va='top', fontsize=10, color='black'
    )
    # Giá trị trung bình
    ax.text(
        i, mean_value * 0.5 if mean_value < 0 else mean_value + (ax.get_ylim()[1] * 0.05),
        f'{mean_value:.2f}',
        ha='center', va='center', fontsize=10, color='white', weight='bold'
    )

# Chú thích ý nghĩa của nose_eye_diff
ax.text(
    0.5, ax.get_ylim()[1] * 0.85,
    'Âm lớn: Mũi gần hơn mắt (Thật)\nGần 0: Bề mặt phẳng (Giả)',
    ha='center', va='top', fontsize=10, color='darkblue', style='italic'
)

# Đặt giới hạn trục y để phù hợp dữ liệu
ax.set_ylim(min(df['nose_eye_diff'].min() * 1.1, -40), max(df['nose_eye_diff'].max() * 1.1, 10) + 5)

plt.tight_layout()

# Hiển thị biểu đồ trong Tkinter
canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.draw()
canvas.get_tk_widget().pack(fill=BOTH, expand=True)

# Chạy giao diện
root.mainloop()