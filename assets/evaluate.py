import os
import numpy as np
from concurrent.futures import ThreadPoolExecutor


class FaceRecognizer:
    def recognize_face(self, face_embedding, known_faces, threshold=1.0):
        best_student_id = "Unknown"
        best_dist = float('inf')

        def compute_distance(db_embedding):
            return np.linalg.norm(face_embedding - db_embedding)

        for student_id, embeddings in known_faces.items():
            with ThreadPoolExecutor() as executor:
                distances = list(executor.map(compute_distance, embeddings))
            min_dist = min(distances)
            if min_dist < best_dist:
                best_dist = min_dist
                best_student_id = student_id

        if best_dist < threshold:
            print(f"Recognized {best_student_id} with distance {best_dist:.2f}")
            return best_student_id, best_dist
        else:
            print(f"No match found (best distance {best_dist:.2f} >= threshold {threshold})")
            return "Unknown", None


# Initialize the recognizer
recognizer = FaceRecognizer()

# Paths to train and test directories
train_dir = "trainData"
test_dir = "testData"

# Step 1: Load known faces from trainData
known_faces = {}
for student_id in os.listdir(train_dir):
    student_dir = os.path.join(train_dir, student_id)
    if not os.path.isdir(student_dir):
        continue
    embeddings = []
    for file_name in os.listdir(student_dir):
        if file_name.endswith(".npy"):
            file_path = os.path.join(student_dir, file_name)
            embedding = np.load(file_path)
            embeddings.append(embedding)
    if embeddings:  # Only add if there are embeddings
        known_faces[student_id] = embeddings

# Step 2: Evaluate on testData
correct = 0
total = 0
for student_id in os.listdir(test_dir):
    student_dir = os.path.join(test_dir, student_id)
    if not os.path.isdir(student_dir):
        continue
    for file_name in os.listdir(student_dir):
        if file_name.endswith(".npy"):
            file_path = os.path.join(student_dir, file_name)
            test_embedding = np.load(file_path)

            # Recognize the face
            predicted_id, distance = recognizer.recognize_face(test_embedding, known_faces, threshold=1.0)

            # Check if prediction is correct
            if predicted_id == student_id:
                correct += 1
            total += 1

# Step 3: Compute accuracy
accuracy = correct / total if total > 0 else 0
print(f"Evaluation complete. Accuracy: {accuracy:.2f} ({correct}/{total})")