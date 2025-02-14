import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import math

# Khởi tạo thư mục lưu embeddings
embedding_dir = "embeddings/"
if not os.path.exists(embedding_dir):
    os.makedirs(embedding_dir)

# Khởi tạo bộ nhận diện khuôn mặt InsightFace
app = FaceAnalysis(allowed_modules=['detection', 'recognition'])
app.prepare(ctx_id=0, det_size=(640, 640))

# Khởi tạo webcam
cap = cv2.VideoCapture(0)

# === Khởi tạo cửa sổ Tkinter ===
root = tk.Tk()
root.title("Face Authentication")
root.geometry("1000x650")
root.configure(bg="#B3E5FC")  # Màu nền xanh biển nhạt

# Biến lưu ID sinh viên
student_id = None

# === NÚT BACK ===
btn_back = tk.Button(root, text="Back", font=("Arial", 12, "bold"), bg="#4699A6", fg="white",
                     width=10, height=2, borderwidth=0, command=root.quit)
btn_back.place(x=30, y=20)

# === TIÊU ĐỀ ===
header_label = tk.Label(root, text="Face Authentication", font=("Arial", 24, "bold"),
                        bg="#B3E5FC", fg="black")
header_label.place(relx=0.5, y=40, anchor="center")

# === KHUNG HIỂN THỊ CAMERA ===
video_frame = tk.Frame(root, width=640, height=400, bg="white", relief="solid", borderwidth=2, highlightbackground="#8A2BE2", highlightthickness=3)
video_frame.place(x=60, y=100)

video_label = tk.Label(video_frame, text="Khung hiển thị camera", font=("Arial", 18, "bold"), bg="white")
video_label.place(relx=0.5, rely=0.5, anchor="center")

# === Ô NHẬP MSSV ===
entry_label = tk.Label(root, text="Enter student ID:", font=("Arial", 14), bg="#B3E5FC", fg="black")
entry_label.place(x=750, y=120)

entry_id = tk.Entry(root, font=("Arial", 14), width=20, bd=2)
entry_id.place(x=750, y=150)

# === KHUNG HIỂN THỊ THÔNG TIN SINH VIÊN ===
info_frame = tk.Frame(root, width=200, height=250, bg="white", relief="solid", borderwidth=2)
info_frame.place(x=750, y=200)

info_label = tk.Label(info_frame, text="hiển thị\nthông tin\nsinh viên", font=("Arial", 14, "bold"), bg="white")
info_label.place(relx=0.5, rely=0.5, anchor="center")

# === NÚT SAVE ===
btn_save = tk.Button(root, text="Save", font=("Arial", 14, "bold"), bg="#4699A6", fg="white",
                     width=10, height=2, borderwidth=0)
btn_save.place(x=800, y=480)

# === HƯỚNG DẪN QUAY MẶT ===
status_label = tk.Label(root, text="📷 Hãy quay mặt thẳng về phía camera",
                        font=("Arial", 12), fg="black", bg="#B3E5FC")
status_label.place(relx=0.5, rely=0.95, anchor="center")


def calculate_face_angle(face):
    """Tính góc nghiêng của khuôn mặt dựa vào hai mắt"""
    landmarks = face.kps  # 5 điểm landmark gồm mắt trái, mắt phải, mũi, miệng trái, miệng phải
    left_eye = landmarks[0]
    right_eye = landmarks[1]

    delta_x = right_eye[0] - left_eye[0]
    delta_y = right_eye[1] - left_eye[1]

    angle = math.degrees(math.atan2(delta_y, delta_x))  # Chuyển đổi sang độ

    return abs(angle)  # Trả về giá trị tuyệt đối của góc


def show_frame():
    """Hiển thị webcam trên giao diện"""
    ret, frame = cap.read()
    if ret:
        faces = app.get(frame)

        if faces:
            for face in faces:
                x1, y1, x2, y2 = map(int, face.bbox)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Kiểm tra góc quay của mặt
                angle = calculate_face_angle(face)
                if angle > 15:
                    status_label.config(text=f"⚠️ Mặt đang nghiêng ({angle:.2f}°), hãy quay thẳng!", fg="red")
                else:
                    status_label.config(text="✅ Mặt thẳng, có thể lưu!", fg="green")

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (640, 400))

        # Chuyển đổi thành ảnh Tkinter
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

    video_label.after(10, show_frame)


def capture_and_save_embedding():
    global student_id
    student_id = entry_id.get().strip()

    if not student_id:
        messagebox.showwarning("⚠️ Lỗi", "Vui lòng nhập MSSV trước khi thu thập!")
        return

    ret, frame = cap.read()
    if not ret:
        messagebox.showerror("❌ Lỗi", "Không thể chụp ảnh từ camera!")
        return

    faces = app.get(frame)

    if faces:
        face = faces[0]

        angle = calculate_face_angle(face)
        if angle <= 15:
            face_embedding = face.normed_embedding
            np.save(os.path.join(embedding_dir, f"{student_id}_embedding.npy"), face_embedding)
            messagebox.showinfo("✅ Thành công", f"Đã lưu embedding cho MSSV {student_id}")
        else:
            status_label.config(text=f"⚠️ Mặt đang nghiêng ({angle:.2f}°), hãy thử lại!", fg="red")
            messagebox.showwarning("⚠️ Lỗi", "Mặt chưa quay thẳng, hãy thử lại!")
    else:
        status_label.config(text="❌ Không phát hiện khuôn mặt!", fg="red")
        messagebox.showerror("❌ Lỗi", "Không tìm thấy khuôn mặt, hãy thử lại!")


def close_app():
    """Thoát chương trình"""
    cap.release()
    cv2.destroyAllWindows()
    root.quit()


btn_save.config(command=capture_and_save_embedding)

# Hiển thị camera trên giao diện
show_frame()

# Chạy giao diện Tkinter
root.mainloop()
