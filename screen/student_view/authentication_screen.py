import os
import math
import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk


class FaceAuthenticationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Authentication")
        self.root.geometry("1000x650")
        self.root.configure(bg="#B3E5FC")  # Light sea blue background

        # Initialize embedding directory
        self.embedding_dir = "../../assets/DataEmbeddings"
        os.makedirs(self.embedding_dir, exist_ok=True)

        # Initialize InsightFace face analysis
        self.app = FaceAnalysis(allowed_modules=['detection', 'recognition'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))

        # Initialize webcam
        self.cap = cv2.VideoCapture(0)

        # Variable to store student ID
        self.student_id = None

        # Initialize GUI
        self.create_widgets()

        self.show_frame()

    def create_widgets(self):
        self.btn_back = tk.Button(self.root, text="Back", font=("Arial", 12, "bold"),
                                  bg="#4699A6", fg="white", width=10, height=2, borderwidth=0,
                                  command=self.close_app)
        self.btn_back.place(x=30, y=20)

        self.header_label = tk.Label(self.root, text="Face Authentication", font=("Arial", 24, "bold"),
                                     bg="#B3E5FC", fg="black")
        self.header_label.place(relx=0.5, y=40, anchor="center")

        self.video_frame = tk.Frame(self.root, width=640, height=400, bg="white", relief="solid",
                                    borderwidth=2, highlightbackground="#8A2BE2", highlightthickness=3)
        self.video_frame.place(x=60, y=100)

        self.video_label = tk.Label(self.video_frame, text="Camera display frame", font=("Arial", 18, "bold"),
                                    bg="white")
        self.video_label.place(relx=0.5, rely=0.5, anchor="center")

        self.entry_label = tk.Label(self.root, text="Enter student ID:", font=("Arial", 14),
                                    bg="#B3E5FC", fg="black")
        self.entry_label.place(x=750, y=120)

        self.entry_id = tk.Entry(self.root, font=("Arial", 14), width=20, bd=2)
        self.entry_id.place(x=750, y=150)

        self.info_frame = tk.Frame(self.root, width=200, height=250, bg="white", relief="solid", borderwidth=2)
        self.info_frame.place(x=750, y=200)

        self.info_label = tk.Label(self.info_frame, text="Student\ninformation", font=("Arial", 14, "bold"), bg="white")
        self.info_label.place(relx=0.5, rely=0.5, anchor="center")

        self.btn_save = tk.Button(self.root, text="Save", font=("Arial", 14, "bold"),
                                  bg="#4699A6", fg="white", width=10, height=2, borderwidth=0,
                                  command=self.capture_and_save_embedding)
        self.btn_save.place(x=800, y=480)
        self.status_label = tk.Label(self.root, text="📷 Please face the camera straight",
                                     font=("Arial", 12), fg="black", bg="#B3E5FC")
        self.status_label.place(relx=0.5, rely=0.95, anchor="center")

    def calculate_face_orientation(self, face):
        """Calculate face orientation (yaw, pitch, roll) using landmarks"""
        landmarks = face.kps  # 5 landmarks: left eye, right eye, nose, left mouth, right mouth
        left_eye = landmarks[0]
        right_eye = landmarks[1]
        nose = landmarks[2]
        left_mouth = landmarks[3]
        right_mouth = landmarks[4]

        # Roll: Angle between eyes (rotation around z-axis)
        delta_x = right_eye[0] - left_eye[0]
        delta_y = right_eye[1] - left_eye[1]
        roll = math.degrees(math.atan2(delta_y, delta_x))

        # Yaw: Estimate left/right tilt using nose position relative to eyes
        eye_midpoint_x = (left_eye[0] + right_eye[0]) / 2
        yaw = (nose[0] - eye_midpoint_x) / (right_eye[0] - left_eye[0]) * 90  # Normalize and scale

        # Pitch: Estimate up/down tilt using vertical nose position relative to eyes and mouth
        eye_midpoint_y = (left_eye[1] + right_eye[1]) / 2
        mouth_midpoint_y = (left_mouth[1] + right_mouth[1]) / 2
        face_height = mouth_midpoint_y - eye_midpoint_y
        nose_relative_y = (nose[1] - eye_midpoint_y) / face_height
        pitch = (nose_relative_y - 0.3) * 100  # Adjust based on typical nose position

        return roll, yaw, pitch

    def classify_orientation(self, roll, yaw, pitch):
        """Classify face orientation based on roll and yaw"""
        roll_threshold = 15  # Degrees
        yaw_threshold = 15  # Degrees

        if abs(roll) <= roll_threshold and abs(yaw) <= yaw_threshold:
            return "straight", "Đang nhìn thẳng"
        elif yaw > yaw_threshold:
            return "right", "Đang nghiêng phải"
        elif yaw < -yaw_threshold:
            return "left", "Đang nghiêng trái"
        else:
            return None, "Adjust face position"

    def show_frame(self):
        ret, frame = self.cap.read()
        if ret:
            faces = self.app.get(frame)

            if faces:
                for face in faces:
                    x1, y1, x2, y2 = map(int, face.bbox)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    roll, yaw, pitch = self.calculate_face_orientation(face)
                    orientation, message = self.classify_orientation(roll, yaw, pitch)

                    if orientation:
                        self.status_label.config(text=f"✅ {message}", fg="green")
                    else:
                        self.status_label.config(text=f"⚠️ {message}", fg="red")

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 400))

            # Convert to Tkinter image
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.video_label.after(10, self.show_frame)

    def capture_and_save_embedding(self):
        """Capture and save face embedding based on orientation, avoiding overwrites"""
        self.student_id = self.entry_id.get().strip()

        if not self.student_id:
            messagebox.showwarning("⚠️ Error", "Please enter student ID before capturing!")
            return

        ret, frame = self.cap.read()
        if not ret:
            messagebox.showerror("❌ Error", "Could not capture image from camera!")
            return

        faces = self.app.get(frame)

        if faces:
            face = faces[0]
            roll, yaw, pitch = self.calculate_face_orientation(face)
            orientation, message = self.classify_orientation(roll, yaw, pitch)

            if orientation:
                student_dir = os.path.join(self.embedding_dir, self.student_id)
                os.makedirs(student_dir, exist_ok=True)

                primary_embedding_path = os.path.join(student_dir, f"{self.student_id}_embedding_{orientation}.npy")

                if os.path.exists(primary_embedding_path):
                    index = 0
                    while True:
                        others_embedding_path = os.path.join(student_dir,
                                                             f"{self.student_id}_embedding_z[{index}].npy")
                        if not os.path.exists(others_embedding_path):
                            break
                        index += 1
                    embedding_path = others_embedding_path
                    display_path = f"{self.student_id}_embedding_z[{index}].npy"
                else:
                    embedding_path = primary_embedding_path
                    display_path = f"{self.student_id}_embedding_{orientation}.npy"

                face_embedding = face.normed_embedding
                np.save(embedding_path, face_embedding)
                messagebox.showinfo("✅ Success", f"Saved embedding as {display_path} (ID: {self.student_id})")
                self.status_label.config(text=f"✅ Saved {display_path}. Try another orientation.", fg="green")
            else:
                self.status_label.config(text=f"⚠️ {message}. Please adjust face!", fg="red")
                messagebox.showwarning("⚠️ Error", "Face orientation not suitable. Please adjust and try again!")
        else:
            self.status_label.config(text="❌ No face detected!", fg="red")
            messagebox.showerror("❌ Error", "No face detected. Please try again!")

    def close_app(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = FaceAuthenticationApp(root)
    root.mainloop()