import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Đọc file CSV từ cùng thư mục
csv_file = '../ChungMinhChonNguong/depth_data_20250424_194815.csv'
try:
    df = pd.read_csv(csv_file)
except FileNotFoundError:
    print(f"Lỗi: Không tìm thấy file '{csv_file}' trong thư mục.")
    exit()

# Tách dữ liệu thành khuôn mặt thật và giả
real_data = df[df['label'] == 'real']
spoof_data = df[df['label'] == 'spoof']

# In thống kê cho khuôn mặt thật
print("Thống kê cho khuôn mặt thật:")
print(f"Chênh lệch mũi-mắt: trung bình = {real_data['nose_eye_diff'].mean():.2f}, độ lệch chuẩn = {real_data['nose_eye_diff'].std():.2f}")
print(f"Độ lệch chuẩn vùng mặt: trung bình = {real_data['face_std_dev'].mean():.2f}, độ lệch chuẩn = {real_data['face_std_dev'].std():.2f}")

# In thống kê cho khuôn mặt giả
print("\nThống kê cho khuôn mặt giả:")
print(f"Chênh lệch mũi-mắt: trung bình = {spoof_data['nose_eye_diff'].mean():.2f}, độ lệch chuẩn = {spoof_data['nose_eye_diff'].std():.2f}")
print(f"Độ lệch chuẩn vùng mặt: trung bình = {spoof_data['face_std_dev'].mean():.2f}, độ lệch chuẩn = {spoof_data['face_std_dev'].std():.2f}")

# Đặt ngưỡng phân loại
nose_eye_diff_threshold = 10  # mm
face_std_dev_threshold = 20   # mm

# Phân loại và tính độ chính xác
# Dùng chỉ face_std_dev
df['predicted_label_std'] = np.where(df['face_std_dev'] > face_std_dev_threshold, 'real', 'spoof')
accuracy_std = (df['label'] == df['predicted_label_std']).mean()
print(f"\nĐộ chính xác dùng face_std_dev > {face_std_dev_threshold}: {accuracy_std:.2f}")

# Dùng chỉ nose_eye_diff
df['predicted_label_diff'] = np.where(df['nose_eye_diff'] > nose_eye_diff_threshold, 'real', 'spoof')
accuracy_diff = (df['label'] == df['predicted_label_diff']).mean()
print(f"Độ chính xác dùng nose_eye_diff > {nose_eye_diff_threshold}: {accuracy_diff:.2f}")

# Dùng cả hai điều kiện
df['predicted_label_both'] = np.where(
    (df['nose_eye_diff'] > nose_eye_diff_threshold) & (df['face_std_dev'] > face_std_dev_threshold),
    'real', 'spoof'
)
accuracy_both = (df['label'] == df['predicted_label_both']).mean()
print(f"Độ chính xác dùng cả hai điều kiện: {accuracy_both:.2f}")

# Vẽ biểu đồ phân phối chênh lệch mũi-mắt
plt.figure(figsize=(10, 6))
sns.histplot(data=df, x='nose_eye_diff', hue='label', kde=True, palette={'real': 'green', 'spoof': 'red'})
plt.axvline(x=nose_eye_diff_threshold, color='k', linestyle='--', label=f'Ngưỡng: {nose_eye_diff_threshold}')
plt.title('Phân phối chênh lệch độ sâu mũi-mắt')
plt.legend()
plt.savefig('nose_eye_diff_histogram.png')
plt.close()

# Vẽ biểu đồ phân phối độ lệch chuẩn vùng mặt
plt.figure(figsize=(10, 6))
sns.histplot(data=df, x='face_std_dev', hue='label', kde=True, palette={'real': 'green', 'spoof': 'red'})
plt.axvline(x=face_std_dev_threshold, color='k', linestyle='--', label=f'Ngưỡng: {face_std_dev_threshold}')
plt.title('Phân phối độ lệch chuẩn độ sâu vùng mặt')
plt.legend()
plt.savefig('face_std_dev_histogram.png')
plt.close()

# Vẽ biểu đồ phân tán
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='nose_eye_diff', y='face_std_dev', hue='label', palette={'real': 'green', 'spoof': 'red'})
plt.axvline(x=nose_eye_diff_threshold, color='k', linestyle='--')
plt.axhline(y=face_std_dev_threshold, color='k', linestyle='--')
plt.title('Biểu đồ phân tán các chỉ số độ sâu với ngưỡng')
plt.savefig('scatter_plot.png')
plt.close()

# Vẽ biểu đồ hộp cho nose_eye_diff
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='label', y='nose_eye_diff', palette={'real': 'lightgreen', 'spoof': 'salmon'})
plt.title('Biểu đồ hộp của chênh lệch mũi-mắt theo nhãn')
plt.savefig('boxplot_nose_eye_diff.png')
plt.close()

# Vẽ biểu đồ hộp cho face_std_dev
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='label', y='face_std_dev', palette={'real': 'lightgreen', 'spoof': 'salmon'})
plt.title('Biểu đồ hộp của độ lệch chuẩn vùng mặt theo nhãn')
plt.savefig('boxplot_face_std_dev.png')
plt.close()

print("\nCác biểu đồ đã được lưu dưới dạng file PNG.")