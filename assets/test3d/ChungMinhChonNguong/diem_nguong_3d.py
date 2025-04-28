import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Thiết lập kiểu dáng biểu đồ
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("talk")
colors = {'real': 'green', 'spoof': 'red'}

# Đọc file CSV
csv_file = 'depth_data.csv'
try:
    df = pd.read_csv(csv_file, delimiter=',', encoding='utf-8', on_bad_lines='skip')
except FileNotFoundError:
    exit()
except Exception as e:
    exit()

# Kiểm tra các cột cần thiết
required_columns = ['face_std_dev', 'nose_eye_diff', 'label']
if not all(col in df.columns for col in required_columns):
    exit()

# Chuyển đổi cột sang kiểu số
df['nose_eye_diff'] = pd.to_numeric(df['nose_eye_diff'], errors='coerce')
df['face_std_dev'] = pd.to_numeric(df['face_std_dev'], errors='coerce')

# Loại bỏ hàng chứa NaN
df = df.dropna(subset=['nose_eye_diff', 'face_std_dev'])

# Tách dữ liệu real và spoof
real_data = df[df['label'] == 'real']
spoof_data = df[df['label'] == 'spoof']

# Định nghĩa ngưỡng
nose_eye_diff_threshold = 15  # mm
face_std_dev_threshold = 25  # mm

# 1. Biểu đồ phân bố (histogram) cho nose_eye_diff
plt.figure(figsize=(10, 6))
plt.hist(real_data['nose_eye_diff'], bins=20, alpha=0.5, label='Real', color='blue')
plt.hist(spoof_data['nose_eye_diff'], bins=20, alpha=0.5, label='Spoof', color='red')

plt.axvline(x=nose_eye_diff_threshold, color='green', linestyle='--', label=f'Ngưỡng {nose_eye_diff_threshold} mm')
plt.text(nose_eye_diff_threshold + 0.5, plt.ylim()[1] * 0.85, f'{nose_eye_diff_threshold}', color='green', fontsize=14, verticalalignment='top')

plt.title('Biểu đồ phân bố chênh lệch mũi - mắt')
plt.xlabel('Chênh lệch mũi - mắt (mm)')
plt.ylabel('Tần suất')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# 2. Biểu đồ phân bố (histogram) cho face_std_dev
plt.figure(figsize=(10, 6))
plt.hist(real_data['face_std_dev'], bins=20, alpha=0.5, label='Real', color='blue')
plt.hist(spoof_data['face_std_dev'], bins=20, alpha=0.5, label='Spoof', color='red')
plt.axvline(x=face_std_dev_threshold, color='green', linestyle='--', label=f'Ngưỡng {face_std_dev_threshold} mm')
plt.text(face_std_dev_threshold + 0.5, plt.ylim()[1] * 0.85, f'{face_std_dev_threshold}', color='green', fontsize=14, verticalalignment='top')
plt.title('Biểu đồ phân bố độ lệch chuẩn vùng mặt')
plt.xlabel('Độ lệch chuẩn vùng mặt (mm)')
plt.ylabel('Tần suất')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()