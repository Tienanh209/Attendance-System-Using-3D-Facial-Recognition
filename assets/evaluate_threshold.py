import pandas as pd
import matplotlib.pyplot as plt
import os

# Định nghĩa ngưỡng
nose_eye_diff_threshold = 15  # mm
face_std_dev_threshold = 25  # mm

# Đọc file CSV
# csv_file = 'test_depth_data.csv'
csv_file = 'depth_data_20250424_194815.csv'
try:
    df = pd.read_csv(csv_file, delimiter=',', encoding='utf-8')
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

# Hàm phân loại dựa trên ngưỡng
def classify_face(row):
    if row['nose_eye_diff'] >= nose_eye_diff_threshold and row['face_std_dev'] >= face_std_dev_threshold:
        return 'real'
    return 'spoof'

# Dự đoán nhãn
df['predicted_label'] = df.apply(classify_face, axis=1)

# Tính độ chính xác
correct = (df['label'] == df['predicted_label']).sum()
total = len(df)
accuracy = correct / total if total > 0 else 0
print(f"Đánh giá hoàn tất. Độ chính xác: {accuracy:.2f} ({correct}/{total})")

# Tính số lượng đúng/sai
correct_count = correct
incorrect_count = total - correct

# Vẽ biểu đồ cột
plt.figure(figsize=(6, 4))
bars = plt.bar(["Chính Xác", "Không Chính Xác"], [correct_count, incorrect_count], color=["green", "red"])
plt.title("Dự Đoán Mặt Thật/Giả")
plt.ylabel("Số Lượng Mẫu Thử")

# Thêm tỷ lệ phần trăm lên cột
for bar in bars:
    height = bar.get_height()
    percentage = (height / total) * 100 if total > 0 else 0
    plt.text(bar.get_x() + bar.get_width() / 2, height, f'{percentage:.1f}%',
             ha='center', va='bottom', fontsize=10, color='black')

# Lưu biểu đồ
output_dir = 'plots'
os.makedirs(output_dir, exist_ok=True)
plt.savefig(os.path.join(output_dir, 'prediction_accuracy.png'), dpi=300)
plt.close()

print(f"Biểu đồ đã được lưu vào '{os.path.join(output_dir, 'prediction_accuracy.png')}'.")