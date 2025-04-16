import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
import os

# Hàm tính khoảng cách Euclidean giữa hai vector
def euclidean_distance(vec1, vec2):
    return np.sqrt(np.sum((vec1 - vec2) ** 2))

# Đường dẫn đến thư mục embeddings
embeddings_path = "DataEmbeddings/"

# Lấy danh sách các thư mục sinh viên
student_dirs = [d for d in os.listdir(embeddings_path) if os.path.isdir(os.path.join(embeddings_path, d))]

# Lưu trữ tất cả embedding của từng sinh viên
all_embeddings = {}
for student in student_dirs:
    student_path = os.path.join(embeddings_path, student)
    embeddings = []
    # Giả định mỗi thư mục sinh viên có 5 file embedding
    for i in range(1, 6):
        file_path = os.path.join(student_path, f"{student}_embedding_{i}.npy")
        if os.path.exists(file_path):
            embedding = np.load(file_path)  # Tải vector 512 chiều
            embeddings.append(embedding)
    all_embeddings[student] = embeddings

# Tính khoảng cách
same_person_distances = []
different_person_distances = []

# Tính khoảng cách "cùng người"
for student, embeddings in all_embeddings.items():
    # Lấy tất cả cặp embedding trong cùng sinh viên
    for (i, j) in combinations(range(len(embeddings)), 2):
        dist = euclidean_distance(embeddings[i], embeddings[j])
        same_person_distances.append(dist)

# Tính khoảng cách "khác người"
student_ids = list(all_embeddings.keys())
for (i, student1) in enumerate(student_ids):
    for student2 in student_ids[i+1:]:
        embeddings1 = all_embeddings[student1]
        embeddings2 = all_embeddings[student2]
        # Tính khoảng cách giữa tất cả cặp embedding của hai sinh viên khác nhau
        for emb1 in embeddings1:
            for emb2 in embeddings2:
                dist = euclidean_distance(emb1, emb2)
                different_person_distances.append(dist)

# Vẽ đồ thị phân bố khoảng cách
plt.figure(figsize=(10, 6))
plt.hist(same_person_distances, bins=20, alpha=0.5, label='Cùng người', color='blue')
plt.hist(different_person_distances, bins=20, alpha=0.5, label='Khác người', color='red')
plt.title('Phân bố khoảng cách Euclidean giữa các embedding')
plt.xlabel('Khoảng cách')
plt.ylabel('Tần suất')
plt.legend()
plt.grid(True)
plt.show()