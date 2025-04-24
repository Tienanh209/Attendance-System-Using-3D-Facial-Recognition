import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Dữ liệu từ file
data = {
    "độ_sâu_mũi": [337, 330, 328, 325, 326, 328, 187, 183, 184, 179, 181, 186, 194, 192, 188, 193],
    "độ_sâu_trung_bình_mắt": [369.5, 361.6666666666667, 354.58333333333337, 346.66666666666663, 352.91666666666663, 356.33333333333337,
                              191.16666666666669, 187.25, 188.33333333333334, 182.0, 183.58333333333334, 189.41666666666666,
                              198.66666666666666, 195.33333333333334, 192.91666666666666, 196.91666666666669],
    "độ_lệch_chuẩn_khuôn_mặt": [274.37977091828776, 254.11598806699402, 237.08409171484365, 206.19354801088463, 203.70630378348392, 150.19675336012872,
                                4.576706547040372, 4.6005134045761595, 3.94454557183227, 3.4951855617134897, 3.702507285718124, 4.064486151194112,
                                4.3549271227739546, 4.319258998654867, 4.269553433968612, 4.161449453661528],
    "chênh_lệch_mũi_mắt": [32.5, 31.666666666666686, 26.58333333333337, 21.66666666666663, 26.91666666666663, 28.33333333333337,
                           4.166666666666686, 4.25, 4.333333333333343, 3.0, 2.583333333333343, 3.416666666666657,
                           4.666666666666657, 3.333333333333343, 4.916666666666657, 3.9166666666666856],
    "nhãn": ["thật", "thật", "thật", "thật", "thật", "thật", "giả", "giả", "giả", "giả", "giả", "giả", "giả", "giả", "giả", "giả"]
}

# Chuyển dữ liệu thành DataFrame
df = pd.DataFrame(data)

# Sử dụng phong cách 'ggplot'
plt.style.use('ggplot')

# 1. Biểu đồ phân tán (Scatter Plot)
plt.figure(figsize=(10, 6))
for nhãn in df['nhãn'].unique():
    subset = df[df['nhãn'] == nhãn]
    plt.scatter(subset['chênh_lệch_mũi_mắt'], subset['độ_lệch_chuẩn_khuôn_mặt'], label=nhãn, s=100, alpha=0.7)
plt.xlabel('Chênh Lệch Độ Sâu Mũi-Mắt (chênh_lệch_mũi_mắt)')
plt.ylabel('Độ Lệch Chuẩn Khuôn Mặt (độ_lệch_chuẩn_khuôn_mặt)')
plt.title('Biểu Đồ Phân Tán: Chênh Lệch Độ Sâu Mũi-Mắt vs Độ Lệch Chuẩn Khuôn Mặt')
plt.legend()
plt.grid(True)
plt.show()

# 2. Biểu đồ hộp (Box Plot) cho chênh_lệch_mũi_mắt và độ_lệch_chuẩn_khuôn_mặt
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# Box Plot cho chênh_lệch_mũi_mắt
sns.boxplot(x='nhãn', y='chênh_lệch_mũi_mắt', data=df, ax=ax1)
ax1.set_title('Biểu Đồ Hộp: Chênh Lệch Độ Sâu Mũi-Mắt Theo Nhãn')
ax1.set_xlabel('Nhãn')
ax1.set_ylabel('Chênh Lệch Độ Sâu Mũi-Mắt')

# Box Plot cho độ_lệch_chuẩn_khuôn_mặt
sns.boxplot(x='nhãn', y='độ_lệch_chuẩn_khuôn_mặt', data=df, ax=ax2)
ax2.set_title('Biểu Đồ Hộp: Độ Lệch Chuẩn Khuôn Mặt Theo Nhãn')
ax2.set_xlabel('Nhãn')
ax2.set_ylabel('Độ Lệch Chuẩn Khuôn Mặt')
plt.tight_layout()
plt.show()

# 3. Biểu đồ cột (Bar Plot) so sánh giá trị trung bình
mean_values = df.groupby('nhãn')[['chênh_lệch_mũi_mắt', 'độ_lệch_chuẩn_khuôn_mặt']].mean()
mean_values.plot(kind='bar', figsize=(10, 6))
plt.title('Giá Trị Trung Bình của Chênh Lệch Độ Sâu Mũi-Mắt và Độ Lệch Chuẩn Khuôn Mặt')
plt.xlabel('Nhãn')
plt.ylabel('Giá Trị Trung Bình')
plt.xticks(rotation=0)
plt.grid(True, axis='y')
plt.show()