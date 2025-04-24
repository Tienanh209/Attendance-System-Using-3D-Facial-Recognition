import json
from time import strftime
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
import mysql.connector
import os
import numpy as np
import pyrealsense2 as rs
import cv2
from insightface.app import FaceAnalysis
from concurrent.futures import ThreadPoolExecutor
import time
import math
import warnings
import dlib
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
warnings.simplefilter("ignore", category=FutureWarning)

class AttendanceSpoofingTest:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1200x700+0+0")
        self.root.title("Spoofing Test with Camera Feed")
        self.isClickedClose = False
        self.spoofing_results = defaultdict(lambda: {"real": 0, "spoof": 0})
        self.angle_increments = 5  # Test ở các góc nghiêng 0, +/- 5, +/- 10, ...
        self.current_test_angle = None
        self.current_test_type = None
        self.test_running = False

        # Khởi tạo RealSense
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.align = rs.align(rs.stream.color)
        try:
            self.pipeline.start(self.config)
        except Exception as e:
            messagebox.showerror("Camera Error", f"Không thể khởi động camera RealSense: {e}")
            self.pipeline = None

        # Khởi tạo InsightFace
        self.app = FaceAnalysis(allowed_modules=['detection'])
        self.app.prepare(ctx_id=-1, det_size=(640, 640))

        # Khởi tạo FaceAntiSpoofing
        self.face_detector = dlib.get_frontal_face_detector()
        self.landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        self.nose_tip_index = 33
        self.left_eye_indices = list(range(36, 42))
        self.right_eye_indices = list(range(42, 48))
        self.tolerance = 15  # Dung sai cho so sánh chiều sâu (mm)
        self.std_dev_threshold = 15  # Ngưỡng độ lệch chuẩn cho vùng khuôn mặt

        self.label_instruction = Label(root, text="Đưa khuôn mặt thật và giả vào camera ở các góc độ khác nhau.", font=("arial", 12))
        self.label_instruction.pack(pady=10)

        self.camera_frame = LabelFrame(root, text="Camera Feed", width=640, height=480)
        self.camera_frame.pack(padx=10, pady=10, side=LEFT)
        self.camera_panel = Label(self.camera_frame)
        self.camera_panel.pack()

        self.controls_frame = Frame(root)
        self.controls_frame.pack(padx=10, pady=10, side=RIGHT, fill=Y)

        self.label_current_test = Label(self.controls_frame, text="Chưa bắt đầu test", font=("arial", 10))
        self.label_current_test.pack(pady=5)

        self.btn_start_test = Button(self.controls_frame, text="Bắt đầu Test Spoofing", command=self.start_test_procedure)
        self.btn_start_test.pack(pady=10)

        self.btn_next_step = Button(self.controls_frame, text="Tiếp tục Bước Test", command=self.next_test_step, state=DISABLED)
        self.btn_next_step.pack(pady=10)

        self.btn_show_chart = Button(self.controls_frame, text="Hiển thị Biểu đồ Kết quả", command=self.show_spoofing_chart, state=DISABLED)
        self.btn_show_chart.pack(pady=10)

        self.text_output = Text(self.controls_frame, height=10, width=40)
        self.text_output.pack(pady=10)

        self.angles_to_test = sorted(list(set([0] + [i * self.angle_increments for i in range(1, 4)] + [-i * self.angle_increments for i in range(1, 4)])))
        self.test_types = ["real", "spoof"]
        self.angle_index = 0
        self.type_index = 0

        self.update_camera_feed()

    def calculate_face_angle_spoofing(self, face):
        landmarks = face.kps
        left_eye = landmarks[0]
        right_eye = landmarks[1]
        delta_x = right_eye[0] - left_eye[0]
        delta_y = right_eye[1] - left_eye[1]
        angle = math.degrees(math.atan2(delta_y, delta_x))
        return angle

    def detect_faces_3d_spoofing(self, color_image, depth_image, faces):
        results = []
        for face in faces:
            box = face.bbox.astype(int)
            dlib_rect = dlib.rectangle(left=box[0], top=box[1], right=box[2], bottom=box[3])
            landmarks = self.landmark_predictor(color_image, dlib_rect)
            landmark_points = [(landmarks.part(n).x, landmarks.part(n).y) for n in range(68)]
            landmark_depths = []
            for x, y in landmark_points:
                if 0 <= x < depth_image.shape[1] and 0 <= y < depth_image.shape[0]:
                    depth = depth_image[y, x]
                    landmark_depths.append(depth)
                else:
                    landmark_depths.append(0)

            valid_depths = [d for d in landmark_depths if d > 0]
            if len(valid_depths) < 0.5 * len(landmark_depths):
                continue

            nose_depth = landmark_depths[self.nose_tip_index]
            left_eye_depths = [landmark_depths[i] for i in self.left_eye_indices if landmark_depths[i] > 0]
            right_eye_depths = [landmark_depths[i] for i in self.right_eye_indices if landmark_depths[i] > 0]
            mean_left_eye_depth = np.mean(left_eye_depths) if left_eye_depths else 0
            mean_right_eye_depth = np.mean(right_eye_depths) if right_eye_depths else 0

            face_region_depth = depth_image[box[1]:box[3], box[0]:box[2]]
            std_dev = np.std(face_region_depth)

            avg_eye_depth = (mean_left_eye_depth + mean_right_eye_depth) / 2 if (mean_left_eye_depth and mean_right_eye_depth) else 0
            is_nose_closer = nose_depth < avg_eye_depth - self.tolerance

            is_real = std_dev > self.std_dev_threshold and is_nose_closer

            results.append({'face': face, 'is_real': is_real})
        return results

    def update_camera_feed(self):
        if self.pipeline and not self.isClickedClose:
            try:
                frames = self.pipeline.wait_for_frames()
                aligned_frames = self.align.process(frames)
                color_frame = aligned_frames.get_color_frame()
                if color_frame:
                    color_image = np.asanyarray(color_frame.get_data())
                    color_image_rgb = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(color_image_rgb)
                    imgtk = ImageTk.PhotoImage(image=img)
                    self.camera_panel.imgtk = imgtk
                    self.camera_panel.config(image=imgtk)
            except Exception as e:
                print(f"Error updating camera feed: {e}")
        self.root.after(30, self.update_camera_feed)

    def start_test_procedure(self):
        if not self.test_running:
            self.test_running = True
            self.spoofing_results.clear()
            self.angle_index = 0
            self.type_index = 0
            self.btn_start_test.config(state=DISABLED)
            self.btn_next_step.config(state=NORMAL)
            self.btn_show_chart.config(state=DISABLED)
            self.next_test_step()

    def next_test_step(self):
        if self.angle_index < len(self.angles_to_test):
            self.current_test_angle = self.angles_to_test[self.angle_index]
            self.current_test_type = self.test_types[self.type_index]
            self.label_current_test.config(text=f"Đưa khuôn mặt {self.current_test_type} vào camera ở góc {self.current_test_angle:.2f} độ.")
            self.text_output.insert(END, f"\n--- Góc: {self.current_test_angle:.2f} độ, Loại: {self.current_test_type} ---\n")
            self.root.update()
            self.perform_detection()

            self.type_index += 1
            if self.type_index >= len(self.test_types):
                self.type_index = 0
                self.angle_index += 1
        else:
            self.label_current_test.config(text="Hoàn thành Test Spoofing")
            self.btn_next_step.config(state=DISABLED)
            self.btn_start_test.config(state=NORMAL)
            self.btn_show_chart.config(state=NORMAL)
            self.test_running = False
            self.text_output.insert(END, "\n--- Hoàn thành Test Spoofing ---\n")

    def perform_detection(self):
        if self.pipeline:
            frames = self.pipeline.wait_for_frames()
            aligned_frames = self.align.process(frames)
            color_frame = aligned_frames.get_color_frame()
            depth_frame = aligned_frames.get_depth_frame()

            if color_frame and depth_frame:
                color_image = np.asanyarray(color_frame.get_data())
                depth_image = np.asanyarray(depth_frame.get_data())
                faces = self.app.get(color_image)

                if faces:
                    for face in faces:
                        face_angle = self.calculate_face_angle_spoofing(face)
                        angle_diff = abs(face_angle - self.current_test_angle)

                        if angle_diff < 10:
                            results_3d = self.detect_faces_3d_spoofing(color_image, depth_image, [face])
                            if results_3d:
                                is_real = results_3d[0]['is_real']
                                prediction = "real" if is_real else "spoof"
                                self.spoofing_results[self.current_test_angle][self.current_test_type] += (1 if prediction == self.current_test_type else 0)
                                self.text_output.insert(END, f"Góc: {face_angle:.2f}, Dự đoán: {prediction}\n")
                            else:
                                self.text_output.insert(END, f"Góc: {face_angle:.2f}, Không đủ dữ liệu 3D.\n")
                        else:
                            self.text_output.insert(END, f"Góc không khớp: {face_angle:.2f} (mục tiêu: {self.current_test_angle:.2f})\n")
                else:
                    self.text_output.insert(END, "Không phát hiện khuôn mặt.\n")
            else:
                self.text_output.insert(END, "Không nhận được khung hình.\n")
        self.root.update()
        time.sleep(1) # Để người dùng có thời gian chuẩn bị cho bước tiếp theo

    def show_spoofing_chart(self):
        angles = sorted(self.spoofing_results.keys())
        real_accuracy = []
        spoof_accuracy = []

        for angle in angles:
            real_correct = self.spoofing_results[angle].get("real", 0)
            spoof_correct = self.spoofing_results[angle].get("spoof", 0)
            total_real = sum(1 for res in self.spoofing_results[angle] if res == "real") if self.spoofing_results[angle].get("real", 0) > 0 else 1 # Tránh chia cho 0
            total_spoof = sum(1 for res in self.spoofing_results[angle] if res == "spoof") if self.spoofing_results[angle].get("spoof", 0) > 0 else 1 # Tránh chia cho 0

            real_acc = (real_correct / total_real) * 100 if total_real > 0 else 0
            spoof_acc = (spoof_correct / total_spoof) * 100 if total_spoof > 0 else 0

            real_accuracy.append(real_acc)
            spoof_accuracy.append(spoof_acc)

        plt.figure(figsize=(10, 6))
        plt.plot(angles, real_accuracy, marker='o', label='Độ chính xác nhận diện khuôn mặt thật')
        plt.plot(angles, spoof_accuracy, marker='x', label='Độ chính xác phát hiện giả mạo')
        plt.xlabel("Góc nghiêng khuôn mặt (độ)")
        plt.ylabel("Tỷ lệ chính xác (%)")
        plt.title("Đánh giá hiệu suất Spoofing theo góc nghiêng")
        plt.xticks(angles)
        plt.ylim(0, 100)
        plt.legend()
        plt.grid(True)
        plt.show()

    def is_clicked(self):
        self.isClickedClose = True
        if self.pipeline:
            self.pipeline.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    root = Tk()
    app = AttendanceSpoofingTest(root)
    root.protocol("WM_DELETE_WINDOW", app.is_clicked)
    root.mainloop()