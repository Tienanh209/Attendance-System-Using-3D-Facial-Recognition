import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
import os

def recognize_face(face_embedding, known_faces, threshold=1.0):
    for student_id, db_embedding in known_faces.items():
        dist = np.linalg.norm(face_embedding - db_embedding)
        if dist < threshold:
            return student_id, dist
    return "Unknown", None

face_db = {}
embedding_dir = 'trainData/'
for file in os.listdir(embedding_dir):
    if file.endswith('_embedding.npy'):
        student_id = file.split('_embedding.npy')[0]
        face_db[student_id] = np.load(os.path.join(embedding_dir, file))

app = FaceAnalysis(allowed_modules=['detection', 'recognition'])
app.prepare(ctx_id=0, det_size=(640, 640))

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()

    faces = app.get(frame)

    for face in faces:
        face_embedding = face.normed_embedding

        student_id, dist = recognize_face(face_embedding, face_db)

        if face.bbox is not None and len(face.bbox) >= 4:
            x1, y1, x2, y2 = map(int, face.bbox)
            cv2.putText(frame, f'{student_id}', (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            frame = app.draw_on(frame, faces)

    cv2.imshow('Camera', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
