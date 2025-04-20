import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
import os

def euclidean_distance(vec1, vec2):
    return np.sqrt(np.sum((vec1 - vec2) ** 2))

embeddings_path = "DataEmbeddings/"

# Lấy danh sách thư mục con (mỗi thư mục là một người)
student_dirs = [d for d in os.listdir(embeddings_path) if os.path.isdir(os.path.join(embeddings_path, d))]

# Lưu tất cả embedding của từng người
all_embeddings = {}
for student in student_dirs:
    student_path = os.path.join(embeddings_path, student)
    embeddings = []
    # Lấy tất cả file .npy trong thư mục của người này
    for file_name in os.listdir(student_path):
        if file_name.endswith(".npy"):
            file_path = os.path.join(student_path, file_name)
            embedding = np.load(file_path)
            embeddings.append(embedding)
    if embeddings:  # Chỉ thêm nếu có embedding
        all_embeddings[student] = embeddings

# Tính khoảng cách Euclidean
same_person_distances = []
different_person_distances = []

# Tính khoảng cách giữa các embedding của cùng một người
for student, embeddings in all_embeddings.items():
    if len(embeddings) > 1:  # Cần ít nhất 2 embedding để tính khoảng cách
        for (i, j) in combinations(range(len(embeddings)), 2):
            dist = euclidean_distance(embeddings[i], embeddings[j])
            same_person_distances.append(dist)

# Tính khoảng cách giữa các embedding của các người khác nhau
student_ids = list(all_embeddings.keys())
for (i, student1) in enumerate(student_ids):
    for student2 in student_ids[i+1:]:
        embeddings1 = all_embeddings[student1]
        embeddings2 = all_embeddings[student2]
        for emb1 in embeddings1:
            for emb2 in embeddings2:
                dist = euclidean_distance(emb1, emb2)
                different_person_distances.append(dist)

# Vẽ biểu đồ phân bố
plt.figure(figsize=(10, 6))
plt.hist(same_person_distances, bins=20, alpha=0.5, label='Cùng người', color='blue')
plt.hist(different_person_distances, bins=20, alpha=0.5, label='Khác người', color='red')

# Đánh dấu đường thẳng tại khoảng cách 1.1
plt.axvline(x=1.1, color='green', linestyle='--', label='Ngưỡng 1.1')
plt.text(1.1 + 0.02, plt.ylim()[1] * 0.85, '1.1', color='green', fontsize=14, verticalalignment='top')

plt.title('Phân bố khoảng cách Euclidean giữa các embedding')
plt.xlabel('Khoảng cách')
plt.ylabel('Tần suất')
plt.legend()
plt.grid(True)
plt.show()