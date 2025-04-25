import os
import math
import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector

class FaceAuthenticationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Authentication")
        self.root.geometry("1000x650")
        self.root.configure(bg="#B3E5FC")  # Light sea blue background

        # Initialize embedding directory
        self.embedding_dir = "../../assets/datasets"
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
        self.entry_id.bind("<Return>", self.fetch_and_display_student_info)

        # Điều chỉnh vị trí và kích thước khung thông tin để không bị che
        self.info_frame = tk.Frame(self.root, width=260, height=280, bg="white", relief="solid", borderwidth=2)
        self.info_frame.place(x=730, y=200)

        # Nhãn tiêu đề "Student Information"
        self.info_title_label = tk.Label(self.info_frame, text="Student Information", font=("Arial", 14, "bold"), bg="white")
        self.info_title_label.place(relx=0.5, y=20, anchor="center")

        # Label hiển thị thông tin sinh viên
        self.info_label = tk.Label(self.info_frame, text="Enter a student ID\nto view information", font=("Arial", 11), bg="white", justify="left", wraplength=240, anchor="w", padx=10)
        self.info_label.place(x=10, y=50)

        # Di chuyển nút Save xuống dưới để không che viền của info_frame
        self.btn_save = tk.Button(self.root, text="Save", font=("Arial", 14, "bold"),
                                  bg="#4699A6", fg="white", width=10, height=2, borderwidth=0,
                                  command=self.capture_and_save_embedding)
        self.btn_save.place(x=800, y=500)  # Di chuyển xuống y=500

        self.status_label = tk.Label(self.root, text="📷 Please face the camera straight",
                                     font=("Arial", 12), fg="black", bg="#B3E5FC")
        self.status_label.place(relx=0.5, rely=0.95, anchor="center")

    def fetch_and_display_student_info(self, event=None):
        """Fetch student information from MySQL database and display it"""
        student_id = self.entry_id.get().strip()

        # Validate student ID format (Bxxxxxxx)
        if not student_id.startswith("B") or len(student_id) != 8 or not student_id[1:].isdigit():
            messagebox.showwarning("⚠️ Error", "Invalid student ID format! It should be Bxxxxxxx (e.g., B1234567)")
            self.info_label.config(text="Enter a student ID\nto view information")
            return

        # Fetch student data from MySQL
        student_data = self.fetch_student_data(student_id)

        if student_data:
            # Format the student information with more spacing and clear labels
            info_text = (
                f"ID: {student_data['id']}\n\n"
                f"Name: {student_data['name']}\n\n"
                f"Birthday: {student_data['birthday']}\n\n"
                f"Email: {student_data['email']}"
            )
            self.info_label.config(text=info_text)
        else:
            messagebox.showerror("❌ Error", f"No student found with ID: {student_id}")
            self.info_label.config(text="Enter a student ID\nto view information")

    def fetch_student_data(self, student_id):
        """Fetch student data from MySQL database"""
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='face_recognition_sys',
                port='3306'
            )
            my_cursor = conn.cursor()
            my_cursor.execute(
                "SELECT id_student, name_student, birthday, email FROM student WHERE id_student = %s",
                (student_id,)
            )
            row = my_cursor.fetchone()
            conn.close()

            if row:
                return {
                    "id": row[0],
                    "name": row[1],
                    "birthday": row[2],
                    "email": row[3]
                }
            return None

        except mysql.connector.Error as err:
            messagebox.showerror("❌ Database Error", f"Error connecting to database: {err}")
            return None

    def calculate_face_orientation(self, face):
        """Calculate face orientation (yaw, pitch, roll) using landmarks"""
        landmarks = face.kps
        left_eye = landmarks[0]
        right_eye = landmarks[1]
        nose = landmarks[2]
        left_mouth = landmarks[3]
        right_mouth = landmarks[4]

        delta_x = right_eye[0] - left_eye[0]
        delta_y = right_eye[1] - left_eye[1]
        roll = math.degrees(math.atan2(delta_y, delta_x))

        eye_midpoint_x = (left_eye[0] + right_eye[0]) / 2
        yaw = (nose[0] - eye_midpoint_x) / (right_eye[0] - left_eye[0]) * 90

        eye_midpoint_y = (left_eye[1] + right_eye[1]) / 2
        mouth_midpoint_y = (left_mouth[1] + right_mouth[1]) / 2
        face_height = mouth_midpoint_y - eye_midpoint_y
        nose_relative_y = (nose[1] - eye_midpoint_y) / face_height
        pitch = (nose_relative_y - 0.3) * 100

        return roll, yaw, pitch

    def classify_orientation(self, roll, yaw, pitch):
        """Classify face orientation based on roll and yaw"""
        roll_threshold = 15
        yaw_threshold = 15

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

            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.video_label.after(10, self.show_frame)

    def capture_and_save_embedding(self):
        """Capture and save face embedding based on orientation with improved file naming"""
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

            if orientation == "straight":
                base_name = f"{self.student_id}_embedding_straight"
            elif orientation == "left":
                base_name = f"{self.student_id}_embedding_left"
            elif orientation == "right":
                base_name = f"{self.student_id}_embedding_right"
            else:
                self.status_label.config(text=f"⚠️ {message}. Please adjust face!", fg="red")
                messagebox.showwarning("⚠️ Error", "Face orientation not suitable. Please adjust and try again!")
                return

            student_dir = os.path.join(self.embedding_dir, self.student_id)
            os.makedirs(student_dir, exist_ok=True)

            index = 0
            while True:
                if index == 0:
                    embedding_path = os.path.join(student_dir, f"{base_name}.npy")
                else:
                    embedding_path = os.path.join(student_dir, f"{base_name}[{index}].npy")

                if not os.path.exists(embedding_path):
                    break
                index += 1

            face_embedding = face.normed_embedding
            np.save(embedding_path, face_embedding)

            if index == 0:
                display_name = f"{base_name}.npy"
            else:
                display_name = f"{base_name}[{index}].npy"

            messagebox.showinfo("✅ Success", f"Saved embedding as {display_name} (ID: {self.student_id})")
            self.status_label.config(text=f"✅ Saved {display_name}. Try another orientation.", fg="green")
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