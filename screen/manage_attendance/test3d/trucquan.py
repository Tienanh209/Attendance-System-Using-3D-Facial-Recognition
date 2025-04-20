import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Dữ liệu từ file
data = {
    "nose_depth": [337, 330, 328, 325, 326, 328, 187, 183, 184, 179, 181, 186, 194, 192, 188, 193],
    "avg_eye_depth": [369.5, 361.6666666666667, 354.58333333333337, 346.66666666666663, 352.91666666666663, 356.33333333333337,
                      191.16666666666669, 187.25, 188.33333333333334, 182.0, 183.58333333333334, 189.41666666666666,
                      198.66666666666666, 195.33333333333334, 192.91666666666666, 196.91666666666669],
    "face_std_dev": [274.37977091828776, 254.11598806699402, 237.08409171484365, 206.19354801088463, 203.70630378348392, 150.19675336012872,
                     4.576706547040372, 4.6005134045761595, 3.94454557183227, 3.4951855617134897, 3.702507285718124, 4.064486151194112,
                     4.3549271227739546, 4.319258998654867, 4.269553433968612, 4.161449453661528],
    "nose_eye_diff": [32.5, 31.666666666666686, 26.58333333333337, 21.66666666666663, 26.91666666666663, 28.33333333333337,
                      4.166666666666686, 4.25, 4.333333333333343, 3.0, 2.583333333333343, 3.416666666666657,
                      4.666666666666657, 3.333333333333343, 4.916666666666657, 3.9166666666666856],
    "label": ["real", "real", "real", "real", "real", "real", "spoof", "spoof", "spoof", "spoof", "spoof", "spoof", "spoof", "spoof", "spoof", "spoof"]
}

# Chuyển dữ liệu thành DataFrame
df = pd.DataFrame(data)

# Sử dụng phong cách 'ggplot' thay vì 'seaborn'
plt.style.use('ggplot')

# 1. Biểu đồ phân tán (Scatter Plot)
plt.figure(figsize=(10, 6))
for label in df['label'].unique():
    subset = df[df['label'] == label]
    plt.scatter(subset['nose_eye_diff'], subset['face_std_dev'], label=label, s=100, alpha=0.7)
plt.xlabel('Nose-Eye Depth Difference (nose_eye_diff)')
plt.ylabel('Face Standard Deviation (face_std_dev)')
plt.title('Scatter Plot: Nose-Eye Depth Difference vs Face Standard Deviation')
plt.legend()
plt.grid(True)
plt.show()

# 2. Biểu đồ hộp (Box Plot) cho nose_eye_diff và face_std_dev
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# Box Plot cho nose_eye_diff
sns.boxplot(x='label', y='nose_eye_diff', data=df, ax=ax1)
ax1.set_title('Box Plot of Nose-Eye Depth Difference by Label')
ax1.set_xlabel('Label')
ax1.set_ylabel('Nose-Eye Depth Difference')

# Box Plot cho face_std_dev
sns.boxplot(x='label', y='face_std_dev', data=df, ax=ax2)
ax2.set_title('Box Plot of Face Standard Deviation by Label')
ax2.set_xlabel('Label')
ax2.set_ylabel('Face Standard Deviation')
plt.tight_layout()
plt.show()

# 3. Biểu đồ cột (Bar Plot) so sánh giá trị trung bình
mean_values = df.groupby('label')[['nose_eye_diff', 'face_std_dev']].mean()
mean_values.plot(kind='bar', figsize=(10, 6))
plt.title('Mean Values of Nose-Eye Depth Difference and Face Standard Deviation')
plt.xlabel('Label')
plt.ylabel('Mean Value')
plt.xticks(rotation=0)
plt.grid(True, axis='y')
plt.show()