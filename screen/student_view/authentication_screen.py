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
        self.root.configure(bg="#B3E5FC")  # Màu nền xanh biển nhạt

        # Khởi tạo thư mục lưu embeddings
        self.embedding_dir = "embeddings/"
        os.makedirs(self.embedding_dir, exist_ok=True)

        # Khởi tạo bộ nhận diện khuôn mặt InsightFace
        self.app = FaceAnalysis(allowed_modules=['detection', 'recognition'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))

        # Khởi tạo webcam
        self.cap = cv2.VideoCapture(0)

        # Biến lưu ID sinh viên
        self.student_id = None

        # Khởi tạo giao diện
        self.create_widgets()

        self.show_frame()

    def create_widgets(self):
        # Nút quay lại
        self.btn_back = tk.Button(self.root, text="Back", font=("Arial", 12, "bold"),
                                  bg="#4699A6", fg="white", width=10, height=2, borderwidth=0,
                                  command=self.close_app)
        self.btn_back.place(x=30, y=20)

        # Tiêu đề
        self.header_label = tk.Label(self.root, text="Face Authentication", font=("Arial", 24, "bold"),
                                     bg="#B3E5FC", fg="black")
        self.header_label.place(relx=0.5, y=40, anchor="center")

        # Khung hiển thị camera
        self.video_frame = tk.Frame(self.root, width=640, height=400, bg="white", relief="solid",
                                    borderwidth=2, highlightbackground="#8A2BE2", highlightthickness=3)
        self.video_frame.place(x=60, y=100)

        self.video_label = tk.Label(self.video_frame, text="Khung hiển thị camera", font=("Arial", 18, "bold"),
                                    bg="white")
        self.video_label.place(relx=0.5, rely=0.5, anchor="center")

        # Ô nhập MSSV
        self.entry_label = tk.Label(self.root, text="Enter student ID:", font=("Arial", 14),
                                    bg="#B3E5FC", fg="black")
        self.entry_label.place(x=750, y=120)

        self.entry_id = tk.Entry(self.root, font=("Arial", 14), width=20, bd=2)
        self.entry_id.place(x=750, y=150)

        # Khung hiển thị thông tin sinh viên
        self.info_frame = tk.Frame(self.root, width=200, height=250, bg="white", relief="solid", borderwidth=2)
        self.info_frame.place(x=750, y=200)

        self.info_label = tk.Label(self.info_frame, text="Thông tin\nsinh viên", font=("Arial", 14, "bold"), bg="white")
        self.info_label.place(relx=0.5, rely=0.5, anchor="center")

        # Nút lưu khuôn mặt
        self.btn_save = tk.Button(self.root, text="Save", font=("Arial", 14, "bold"),
                                  bg="#4699A6", fg="white", width=10, height=2, borderwidth=0,
                                  command=self.capture_and_save_embedding)
        self.btn_save.place(x=800, y=480)

        # Hướng dẫn quay mặt
        self.status_label = tk.Label(self.root, text="📷 Hãy quay mặt thẳng về phía camera",
                                     font=("Arial", 12), fg="black", bg="#B3E5FC")
        self.status_label.place(relx=0.5, rely=0.95, anchor="center")

    def calculate_face_angle(self, face):
        landmarks = face.kps  # 5 điểm landmark gồm mắt trái, mắt phải, mũi, miệng trái, miệng phải
        left_eye = landmarks[0]
        right_eye = landmarks[1]

        delta_x = right_eye[0] - left_eye[0]
        delta_y = right_eye[1] - left_eye[1]

        angle = math.degrees(math.atan2(delta_y, delta_x))  # Chuyển đổi sang độ

        return abs(angle)  # Trả về giá trị tuyệt đối của góc

    def show_frame(self):
        ret, frame = self.cap.read()
        if ret:
            faces = self.app.get(frame)

            if faces:
                for face in faces:
                    x1, y1, x2, y2 = map(int, face.bbox)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    # Kiểm tra góc quay của mặt
                    angle = self.calculate_face_angle(face)
                    if angle > 15:
                        self.status_label.config(text=f"⚠️ Mặt đang nghiêng ({angle:.2f}°), hãy quay thẳng!", fg="red")
                    else:
                        self.status_label.config(text="✅ Mặt thẳng, có thể lưu!", fg="green")

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 400))

            # Chuyển đổi thành ảnh Tkinter
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.video_label.after(10, self.show_frame)

    def capture_and_save_embedding(self):
        """Chụp ảnh và lưu embedding khuôn mặt"""
        self.student_id = self.entry_id.get().strip()

        if not self.student_id:
            messagebox.showwarning("⚠️ Lỗi", "Vui lòng nhập MSSV trước khi thu thập!")
            return

        ret, frame = self.cap.read()
        if not ret:
            messagebox.showerror("❌ Lỗi", "Không thể chụp ảnh từ camera!")
            return

        faces = self.app.get(frame)

        if faces:
            face = faces[0]

            angle = self.calculate_face_angle(face)
            if angle <= 15:
                face_embedding = face.normed_embedding
                np.save(os.path.join(self.embedding_dir, f"{self.student_id}_embedding.npy"), face_embedding)
                messagebox.showinfo("✅ Thành công", f"Đã lưu embedding cho MSSV {self.student_id}")
            else:
                self.status_label.config(text=f"⚠️ Mặt đang nghiêng ({angle:.2f}°), hãy thử lại!", fg="red")
                messagebox.showwarning("⚠️ Lỗi", "Mặt chưa quay thẳng, hãy thử lại!")
        else:
            self.status_label.config(text="❌ Không phát hiện khuôn mặt!", fg="red")
            messagebox.showerror("❌ Lỗi", "Không tìm thấy khuôn mặt, hãy thử lại!")

    def close_app(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceAuthenticationApp(root)
    root.mainloop()
#
# import os
# import math
# import cv2
# import numpy as np
# import insightface
# from insightface.app import FaceAnalysis
# import tkinter as tk
# from tkinter import messagebox
# from PIL import Image, ImageTk
#
#
# class FaceAuthenticationApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Face Authentication")
#         self.root.geometry("1000x650")
#         self.root.configure(bg="#B3E5FC")  # Màu nền xanh biển nhạt
#
#         # Khởi tạo thư mục lưu embeddings
#         self.embedding_dir = "embeddings/"
#         os.makedirs(self.embedding_dir, exist_ok=True)
#
#         # Khởi tạo bộ nhận diện khuôn mặt InsightFace
#         self.app = FaceAnalysis(allowed_modules=['detection', 'recognition'])
#         self.app.prepare(ctx_id=0, det_size=(640, 640))
#
#         # Khởi tạo webcam
#         self.cap = cv2.VideoCapture(0)
#
#         # Biến lưu ID sinh viên
#         self.student_id = None
#
#         # Khởi tạo giao diện
#         self.create_widgets()
#
#         self.show_frame()
#
#     def create_widgets(self):
#         # Nút quay lại
#         self.btn_back = tk.Button(self.root, text="Back", font=("Arial", 12, "bold"),
#                                   bg="#4699A6", fg="white", width=10, height=2, borderwidth=0,
#                                   command=self.close_app, relief="ridge")
#         self.btn_back.place(x=30, y=20)
#
#         self.btn_back.configure(highlightbackground="#4699A6", highlightthickness=2, relief="ridge")
#         self.btn_back.config(borderwidth=2, padx=5, pady=2, bd=2, relief="ridge")
#
#         # Tiêu đề
#         self.header_label = tk.Label(self.root, text="Face Authentication", font=("Arial", 24, "bold"),
#                                      bg="#B3E5FC", fg="black")
#         self.header_label.place(relx=0.5, y=40, anchor="center")
#
#         # Khung hiển thị camera
#         self.video_frame = tk.Frame(self.root, width=640, height=400, bg="white", relief="solid",
#                                     borderwidth=2, highlightbackground="#8A2BE2", highlightthickness=3)
#         self.video_frame.place(x=60, y=100)
#
#         self.video_label = tk.Label(self.video_frame, text="Khung hiển thị camera", font=("Arial", 18, "bold"),
#                                     bg="white")
#         self.video_label.place(relx=0.5, rely=0.5, anchor="center")
#
#         # Ô nhập MSSV
#         self.entry_label = tk.Label(self.root, text="Enter student ID:", font=("Arial", 14),
#                                     bg="#B3E5FC", fg="black")
#         self.entry_label.place(x=750, y=120)
#
#         self.entry_id = tk.Entry(self.root, font=("Arial", 14), width=20, bd=2)
#         self.entry_id.place(x=750, y=150)
#
#         # Khung hiển thị thông tin sinh viên
#         self.info_frame = tk.Frame(self.root, width=200, height=250, bg="white", relief="solid", borderwidth=2)
#         self.info_frame.place(x=750, y=200)
#
#         self.info_label = tk.Label(self.info_frame, text="Thông tin\nsinh viên", font=("Arial", 14, "bold"), bg="white")
#         self.info_label.place(relx=0.5, rely=0.5, anchor="center")
#
#         # Nút lưu khuôn mặt
#         self.btn_save = tk.Button(self.root, text="Save", font=("Arial", 14, "bold"),
#                                   bg="#4699A6", fg="white", width=10, height=2, borderwidth=0,
#                                   command=self.capture_and_save_embedding, relief="ridge")
#         self.btn_save.place(x=800, y=480)
#
#         self.btn_save.configure(highlightbackground="#4699A6", highlightthickness=2, relief="ridge")
#         self.btn_save.config(borderwidth=2, padx=5, pady=2, bd=2, relief="ridge")
#
#         # Hướng dẫn quay mặt
#         self.status_label = tk.Label(self.root, text="📷 Hãy quay mặt thẳng về phía camera",
#                                      font=("Arial", 12), fg="black", bg="#B3E5FC")
#         self.status_label.place(relx=0.5, rely=0.95, anchor="center")
#
#     def calculate_face_angle(self, face):
#         landmarks = face.kps
#         left_eye = landmarks[0]
#         right_eye = landmarks[1]
#
#         delta_x = right_eye[0] - left_eye[0]
#         delta_y = right_eye[1] - left_eye[1]
#
#         angle = math.degrees(math.atan2(delta_y, delta_x))
#         return abs(angle)
#
#     def show_frame(self):
#         ret, frame = self.cap.read()
#         if ret:
#             faces = self.app.get(frame)
#
#             if faces:
#                 for face in faces:
#                     x1, y1, x2, y2 = map(int, face.bbox)
#                     cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#
#                     angle = self.calculate_face_angle(face)
#                     if angle > 15:
#                         self.status_label.config(text=f"⚠️ Mặt đang nghiêng ({angle:.2f}°), hãy quay thẳng!", fg="red")
#                     else:
#                         self.status_label.config(text="✅ Mặt thẳng, có thể lưu!", fg="green")
#
#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             frame = cv2.resize(frame, (640, 400))
#
#             img = Image.fromarray(frame)
#             imgtk = ImageTk.PhotoImage(image=img)
#             self.video_label.imgtk = imgtk
#             self.video_label.configure(image=imgtk)
#
#         self.video_label.after(10, self.show_frame)
#
#     def capture_and_save_embedding(self):
#         self.student_id = self.entry_id.get().strip()
#         if not self.student_id:
#             messagebox.showwarning("⚠️ Lỗi", "Vui lòng nhập MSSV trước khi thu thập!")
#             return
#
#         ret, frame = self.cap.read()
#         if not ret:
#             messagebox.showerror("❌ Lỗi", "Không thể chụp ảnh từ camera!")
#             return
#
#         faces = self.app.get(frame)
#         if faces:
#             face = faces[0]
#             angle = self.calculate_face_angle(face)
#             if angle <= 15:
#                 face_embedding = face.normed_embedding
#                 np.save(os.path.join(self.embedding_dir, f"{self.student_id}_embedding.npy"), face_embedding)
#                 messagebox.showinfo("✅ Thành công", f"Đã lưu embedding cho MSSV {self.student_id}")
#             else:
#                 self.status_label.config(text=f"⚠️ Mặt đang nghiêng ({angle:.2f}°), hãy thử lại!", fg="red")
#                 messagebox.showwarning("⚠️ Lỗi", "Mặt chưa quay thẳng, hãy thử lại!")
#         else:
#             self.status_label.config(text="❌ Không phát hiện khuôn mặt!", fg="red")
#             messagebox.showerror("❌ Lỗi", "Không tìm thấy khuôn mặt, hãy thử lại!")
#
#     def close_app(self):
#         self.cap.release()
#         cv2.destroyAllWindows()
#         self.root.quit()
#
#
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = FaceAuthenticationApp(root)
#     root.mainloop()