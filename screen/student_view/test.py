import numpy as np

# Đường dẫn đến file
file_path = "../../assets/AntiSpoofing_DT/antispoof_2.npy"

# Đọc file
data = np.load(file_path, allow_pickle=True).item()

# In nội dung
print("Dữ liệu từ file:", file_path)
print("landmark_points:", data['landmark_points'].shape)
print("landmark_depths:", data['landmark_depths'].shape)
print("nose_depth:", data['nose_depth'])
print("mean_left_eye_depth:", data['mean_left_eye_depth'])
print("mean_right_eye_depth:", data['mean_right_eye_depth'])
print("mean_jaw_depth:", data['mean_jaw_depth'])
print("std_dev:", data['std_dev']) 