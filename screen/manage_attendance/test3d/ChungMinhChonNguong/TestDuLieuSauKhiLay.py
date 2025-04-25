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
    print(f"Đã đọc thành công file '{csv_file}'.")
except FileNotFoundError:
    print(f"Lỗi: Không tìm thấy file '{csv_file}'.")
    exit()
except Exception as e:
    print(f"Lỗi khi đọc file CSV: {e}")
    exit()

# Kiểm tra các cột cần thiết
required_columns = ['face_std_dev', 'nose_eye_diff', 'label']
if not all(col in df.columns for col in required_columns):
    print(f"Lỗi: File CSV phải chứa các cột: {required_columns}.")
    exit()

# Chuyển đổi cột sang kiểu số
df['nose_eye_diff'] = pd.to_numeric(df['nose_eye_diff'], errors='coerce')
df['face_std_dev'] = pd.to_numeric(df['face_std_dev'], errors='coerce')

# Loại bỏ hàng chứa NaN
initial_len = len(df)
df = df.dropna(subset=['nose_eye_diff', 'face_std_dev'])
if len(df) < initial_len:
    print(f"Cảnh báo: Đã loại bỏ {initial_len - len(df)} hàng chứa giá trị NaN.")

# Tách dữ liệu real và spoof
real_data = df[df['label'] == 'real']
spoof_data = df[df['label'] == 'spoof']

# Tính toán thống kê
total_samples = len(df)
real_count = len(real_data)
spoof_count = len(spoof_data)
stats = {
    'nose_eye_diff': {
        'real': real_data['nose_eye_diff'].mean(),
        'spoof': spoof_data['nose_eye_diff'].mean()
    },
    'face_std_dev': {
        'real': real_data['face_std_dev'].mean(),
        'spoof': spoof_data['face_std_dev'].mean()
    }
}

# In thống kê
print("Thống kê dữ liệu:")
print(f"  Tổng số mẫu: {total_samples}")
print(f"  Số mẫu Real: {real_count}")
print(f"  Số mẫu Spoof: {spoof_count}")
print(
    f"  Chênh lệch mũi-mắt trung bình (mm): Real = {stats['nose_eye_diff']['real']:.2f}, Spoof = {stats['nose_eye_diff']['spoof']:.2f}")
print(
    f"  Độ lệch chuẩn vùng mặt trung bình (mm): Real = {stats['face_std_dev']['real']:.2f}, Spoof = {stats['face_std_dev']['spoof']:.2f}")

# Tạo thư mục lưu biểu đồ
output_dir = 'plots'
os.makedirs(output_dir, exist_ok=True)

# Định nghĩa ngưỡng
nose_eye_diff_threshold = 15  # mm
face_std_dev_threshold = 25  # mm

# 1. Biểu đồ scatter plot cho nose_eye_diff
plt.figure(figsize=(10, 6))
plt.scatter(real_data.index, real_data['nose_eye_diff'], s=50, color=colors['real'], label='Real', alpha=0.6)
plt.scatter(spoof_data.index, spoof_data['nose_eye_diff'], s=50, color=colors['spoof'], label='Spoof', alpha=0.6)
plt.axhline(y=nose_eye_diff_threshold, color='black', linestyle='--', label=f'Ngưỡng: {nose_eye_diff_threshold} mm')
plt.xlabel('Chỉ số mẫu')
plt.ylabel('Chênh lệch mũi-mắt (mm)')
plt.title('Biểu đồ phân tán của chênh lệch mũi-mắt')
plt.ylim(min(df['nose_eye_diff'].min(), 0), max(df['nose_eye_diff'].max(), nose_eye_diff_threshold))
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'scatter_nose_eye_diff.png'), dpi=300)
plt.close()

# 2. Biểu đồ scatter plot cho face_std_dev
plt.figure(figsize=(10, 6))
plt.scatter(real_data.index, real_data['face_std_dev'], s=50, color=colors['real'], label='Real', alpha=0.6)
plt.scatter(spoof_data.index, spoof_data['face_std_dev'], s=50, color=colors['spoof'], label='Spoof', alpha=0.6)
plt.axhline(y=face_std_dev_threshold, color='black', linestyle='--', label=f'Ngưỡng: {face_std_dev_threshold} mm')
plt.xlabel('Chỉ số mẫu')
plt.ylabel('Độ lệch chuẩn vùng mặt (mm)')
plt.title('Biểu đồ phân tán của độ lệch chuẩn vùng mặt')
plt.ylim(min(df['face_std_dev'].min(), 0), max(df['face_std_dev'].max(), face_std_dev_threshold))
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'scatter_face_std_dev.png'), dpi=300)
plt.close()

print("\nCác biểu đồ đã được lưu dưới dạng file PNG trong thư mục 'plots'.")