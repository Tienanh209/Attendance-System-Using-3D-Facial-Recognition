import os
import numpy as np
import cv2
import pyrealsense2 as rs
import dlib
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class FaceAntiSpoofingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Anti-Spoofing Data Collection")
        self.root.geometry("1000x650")
        self.root.configure(bg="#B3E5FC")  # Màu nền xanh biển nhạt

        # Khởi tạo thư mục lưu dữ liệu
        self.data_dir = "../../assets/AntiSpoofing_DT"
        os.makedirs(self.data_dir, exist_ok=True)

        # Thiết lập camera RealSense
        self.pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.profile = self.pipeline.start(config)
        self.align = rs.align(rs.stream.color)

        # Tải mô hình dlib
        self.face_detector = dlib.get_frontal_face_detector()
        self.landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

        # Định nghĩa chỉ số điểm mốc
        self.nose_tip_index = 33
        self.left_eye_indices = list(range(36, 42))
        self.right_eye_indices = list(range(42, 48))
        self.jaw_indices = list(range(0, 17))

        # Khởi tạo giao diện
        self.create_widgets()

        # Bắt đầu hiển thị video
        self.show_frame()

    def create_widgets(self):
        # Nút quay lại
        self.btn_back = tk.Button(self.root, text="Back", font=("Arial", 12, "bold"),
                                  bg="#4699A6", fg="white", width=10, height=2, borderwidth=0,
                                  command=self.close_app)
        self.btn_back.place(x=30, y=20)

        # Tiêu đề
        self.header_label = tk.Label(self.root, text="Face Anti-Spoofing", font=("Arial", 24, "bold"),
                                     bg="#B3E5FC", fg="black")
        self.header_label.place(relx=0.5, y=40, anchor="center")

        # Khung hiển thị camera
        self.video_frame = tk.Frame(self.root, width=640, height=400, bg="white", relief="solid",
                                    borderwidth=2, highlightbackground="#8A2BE2", highlightthickness=3)
        self.video_frame.place(x=60, y=100)

        self.video_label = tk.Label(self.video_frame, text="Khung hiển thị camera", font=("Arial", 18, "bold"),
                                    bg="white")
        self.video_label.place(relx=0.5, rely=0.5, anchor="center")

        # Nút lưu dữ liệu
        self.btn_save = tk.Button(self.root, text="Save", font=("Arial", 14, "bold"),
                                  bg="#4699A6", fg="white", width=10, height=2, borderwidth=0,
                                  command=self.capture_and_save_data)
        self.btn_save.place(x=800, y=280)

        # Nhãn trạng thái
        self.status_label = tk.Label(self.root, text="📷 Hãy nhìn thẳng vào camera",
                                     font=("Arial", 12), fg="black", bg="#B3E5FC")
        self.status_label.place(relx=0.5, rely=0.95, anchor="center")

    def process_frame(self):
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()

        if not color_frame or not depth_frame:
            return None

        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        return color_image, depth_image

    def detect_faces(self, color_image, depth_image):
        faces = self.face_detector(color_image)
        results = []

        for face in faces:
            landmarks = self.landmark_predictor(color_image, face)
            landmark_points = [(landmarks.part(n).x, landmarks.part(n).y) for n in range(68)]

            landmark_depths = []
            for x, y in landmark_points:
                if 0 <= x < depth_image.shape[1] and 0 <= y < depth_image.shape[0]:
                    depth = depth_image[y, x]
                    landmark_depths.append(depth)
                else:
                    landmark_depths.append(0)

            nose_depth = landmark_depths[self.nose_tip_index]
            mean_left_eye_depth = np.mean([landmark_depths[i] for i in self.left_eye_indices if landmark_depths[i] > 0])
            mean_right_eye_depth = np.mean([landmark_depths[i] for i in self.right_eye_indices if landmark_depths[i] > 0])
            mean_jaw_depth = np.mean([landmark_depths[i] for i in self.jaw_indices if landmark_depths[i] > 0])

            face_region_depth = depth_image[face.top():face.bottom(), face.left():face.right()]
            std_dev = np.std(face_region_depth)

            results.append({
                'face': face,
                'landmark_points': np.array(landmark_points),
                'landmark_depths': np.array(landmark_depths),
                'nose_depth': nose_depth,
                'mean_left_eye_depth': mean_left_eye_depth,
                'mean_right_eye_depth': mean_right_eye_depth,
                'mean_jaw_depth': mean_jaw_depth,
                'std_dev': std_dev
            })

        return results

    def show_frame(self):
        result = self.process_frame()
        if result is None:
            self.video_label.after(10, self.show_frame)
            return

        color_image, depth_image = result
        face_results = self.detect_faces(color_image, depth_image)

        for result in face_results:
            face = result['face']
            cv2.rectangle(color_image, (face.left(), face.top()), (face.right(), face.bottom()), (0, 255, 0), 2)
            cv2.putText(color_image, "Face Detected", (face.left(), face.top() - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # Vẽ các điểm mốc
            for x, y in result['landmark_points']:
                cv2.circle(color_image, (int(x), int(y)), 2, (255, 0, 0), -1)

            self.status_label.config(text="✅ Face detected!", fg="green")

        if not face_results:
            self.status_label.config(text="❌ No face detected!", fg="red")

        color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
        color_image = cv2.resize(color_image, (640, 400))

        img = Image.fromarray(color_image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

        self.video_label.after(10, self.show_frame)

    def capture_and_save_data(self):
        result = self.process_frame()
        if result is None:
            messagebox.showerror("❌ Lỗi", "Không thể chụp ảnh từ camera!")
            return

        color_image, depth_image = result
        face_results = self.detect_faces(color_image, depth_image)

        if not face_results:
            self.status_label.config(text="❌ Không phát hiện khuôn mặt!", fg="red")
            messagebox.showerror("❌ Lỗi", "Không tìm thấy khuôn mặt, hãy thử lại!")
            return

        result = face_results[0]  # Lấy khuôn mặt đầu tiên

        data_count = len(os.listdir(self.data_dir)) + 1
        data_path = os.path.join(self.data_dir, f"antispoof_{data_count}.npy")

        data_to_save = {
            'landmark_points': result['landmark_points'],
            'landmark_depths': result['landmark_depths'],
            'nose_depth': result['nose_depth'],
            'mean_left_eye_depth': result['mean_left_eye_depth'],
            'mean_right_eye_depth': result['mean_right_eye_depth'],
            'mean_jaw_depth': result['mean_jaw_depth'],
            'std_dev': result['std_dev']
        }

        np.save(data_path, data_to_save)
        self.status_label.config(text="✅ Đã lưu dữ liệu!", fg="green")
        messagebox.showinfo("✅ Thành công", "Đã lưu dữ liệu!")

    def close_app(self):
        self.pipeline.stop()
        cv2.destroyAllWindows()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceAntiSpoofingApp(root)
    root.mainloop()