import os
import numpy as np
import matplotlib.pyplot as plt

# Thư mục chứa dữ liệu
data_dir = "../../assets/AntiSpoofing_DT"

# Danh sách để lưu tolerance và std_dev
tolerances = []
std_devs = []

# Đọc dữ liệu từ các file .npy
for file_name in os.listdir(data_dir):
    if not file_name.endswith(".npy"):
        continue

    file_path = os.path.join(data_dir, file_name)
    try:
        # Đọc file .npy
        data = np.load(file_path, allow_pickle=True).item()

        # Trích xuất tolerance (nose_eye_diff) và std_dev
        tolerance = data.get('nose_eye_diff', 0)
        std_dev = data.get('std_dev', 0)

        # Lưu vào danh sách nếu giá trị hợp lệ
        if tolerance != 0:
            tolerances.append(tolerance)
        if std_dev != 0:
            std_devs.append(std_dev)

        print(f"Processed {file_name}: tolerance={tolerance:.2f}, std_dev={std_dev:.2f}")

    except Exception as e:
        print(f"Error processing {file_name}: {e}")

# Kiểm tra dữ liệu
if not tolerances or not std_devs:
    print("No valid data to plot.")
    exit()

# Vẽ biểu đồ
plt.figure(figsize=(12, 5))

# Biểu đồ 1: Scatter Plot
plt.subplot(1, 2, 1)
plt.scatter(tolerances, std_devs, color="blue", alpha=0.5)
plt.title("Tolerance vs Std Dev")
plt.xlabel("Tolerance (mm)")
plt.ylabel("Std Dev (mm)")
plt.grid(True)

# Biểu đồ 2: Box Plot
plt.subplot(1, 2, 2)
plt.boxplot([tolerances, std_devs], labels=["Tolerance", "Std Dev"], patch_artist=True,
            boxprops=dict(facecolor="lightblue", color="blue"),
            medianprops=dict(color="red"))
plt.title("Distribution of Tolerance and Std Dev")
plt.ylabel("Value (mm)")

# Điều chỉnh layout và hiển thị
plt.tight_layout()
plt.show()