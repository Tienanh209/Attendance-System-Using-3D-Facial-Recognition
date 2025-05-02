import os
import numpy as np
from tkinter import Tk, Label, Button, StringVar
from insightface.app import FaceAnalysis
import cv2
import glob


class traindata:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Data Training")
        self.status_var = StringVar()
        self.status_var.set("Ready to process data.")

        # UI Components
        self.status_label = Label(root, textvariable=self.status_var, font=("Arial", 14))
        self.status_label.pack(pady=20)

        self.process_button = Button(root, text="Start Training", command=self.train_data, font=("Arial", 14),
                                     bg="green", fg="white")
        self.process_button.pack(pady=10)

        self.exit_button = Button(root, text="Exit", command=root.quit, font=("Arial", 14), bg="red", fg="white")
        self.exit_button.pack(pady=10)

    def train_data(self):
        self.status_var.set("Processing...")
        self.root.update()  # Update the UI

        # FaceAnalysis Initialization
        app = FaceAnalysis(allowed_modules=['detection', 'recognition'])
        app.prepare(ctx_id=1, det_size=(640, 640))

        data_dir = '../../assets/Data/'
        embedding_dir = '../../DataEmbeddings/'

        if not os.path.exists(embedding_dir):
            os.makedirs(embedding_dir)

        face_db = {}

        for student_id in os.listdir(data_dir):
            student_dir = os.path.join(data_dir, student_id)
            img_paths = glob.glob(os.path.join(student_dir, '*.jpg'))

            if len(img_paths) > 0:
                for img_path in img_paths:
                    img = cv2.imread(img_path)
                    faces = app.get(img)

                    if len(faces) > 0:
                        face_embedding = faces[0].normed_embedding  # Extract feature
                        face_db[student_id] = face_embedding

                        embedding_path = os.path.join(embedding_dir, f'{student_id}_embedding.npy')
                        np.save(embedding_path, face_embedding)  # Save embedding

        self.status_var.set(f"Training complete. Embeddings saved in '{embedding_dir}'.")
        self.root.update()


if __name__ == "__main__":
    root = Tk()
    app = traindata(root)
    root.mainloop()
