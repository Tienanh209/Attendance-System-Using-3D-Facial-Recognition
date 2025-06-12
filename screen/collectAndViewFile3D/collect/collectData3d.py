# import pyrealsense2 as rs
# import numpy as np
# import dlib
# import cv2
# import csv
# import os
# import tkinter as tk
# from tkinter import ttk, simpledialog, messagebox
# from PIL import Image, ImageTk
# import threading
# import time
# import json
#
#
# class Face3DAnalysisApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("3D Face Analysis")
#         self.root.geometry("1000x700")
#         self.root.configure(bg="#f0f0f0")
#
#         # Khởi tạo biến
#         self.person_id = ""
#         self.session_id = time.strftime("%Y%m%d_%H%M%S")
#         self.frame_number = 0
#         self.landmark_3d = None
#         self.current_image = None
#         self.display_image = None
#         self.running = False
#         self.show_landmarks = tk.BooleanVar(value=True)
#         self.continuous_capture = tk.BooleanVar(value=False)
#         self.capture_interval = tk.IntVar(value=3)  # seconds
#         self.last_capture_time = 0
#
#         # Tạo thư mục lưu trữ
#         self.base_folder = "FileObject3D"
#         if not os.path.exists(self.base_folder):
#             os.makedirs(self.base_folder)
#
#         # Tạo layout
#         self.create_layout()
#
#         # Khởi tạo Intel RealSense
#         try:
#             self.pipeline = rs.pipeline()
#             self.config = rs.config()
#             self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
#             self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
#             self.align = rs.align(rs.stream.color)
#             self.pipeline.start(self.config)
#             self.status_label.config(text="Status: Camera initialized")
#         except Exception as e:
#             self.status_label.config(text=f"Error initializing camera: {e}")
#             messagebox.showerror("Camera Error", f"Failed to initialize RealSense camera: {e}")
#
#         # Khởi tạo Dlib
#         try:
#             self.face_detector = dlib.get_frontal_face_detector()
#             model_path = "../../manage_attendance/shape_predictor_68_face_landmarks.dat"
#             if not os.path.exists(model_path):
#                 self.status_label.config(text="Error: Missing shape_predictor_68_face_landmarks.dat")
#                 messagebox.showerror("Error",
#                                      "Missing face landmark model file.\nPlease download shape_predictor_68_face_landmarks.dat")
#             else:
#                 self.landmark_predictor = dlib.shape_predictor(model_path)
#                 self.status_label.config(text="Status: Dlib initialized")
#         except Exception as e:
#             self.status_label.config(text=f"Error initializing Dlib: {e}")
#             messagebox.showerror("Dlib Error", f"Failed to initialize face detector: {e}")
#
#         # Landmark group definitions
#         self.landmark_groups = {
#             "jaw": list(range(0, 17)),
#             "eyebrows": list(range(17, 27)),
#             "nose": list(range(27, 36)),
#             "left_eye": list(range(36, 42)),
#             "right_eye": list(range(42, 48)),
#             "mouth_outer": list(range(48, 60)),
#             "mouth_inner": list(range(60, 68))
#         }
#
#         # Khởi tạo InsightFace (nếu cần)
#         try:
#             from insightface.app import FaceAnalysis
#             self.app = FaceAnalysis(allowed_modules=['detection', 'recognition'])
#             self.app.prepare(ctx_id=0, det_size=(640, 640))
#             self.use_insightface = True
#         except:
#             self.use_insightface = False
#             print("InsightFace not available, skipping...")
#
#         # Bắt đầu cập nhật video
#         self.update_video()
#
#     def create_layout(self):
#         # Main container
#         main_frame = ttk.Frame(self.root)
#         main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
#
#         # Left panel - Camera feed
#         left_frame = ttk.Frame(main_frame)
#         left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
#
#         # Camera canvas with border
#         canvas_frame = ttk.LabelFrame(left_frame, text="Camera Feed")
#         canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
#
#         self.canvas = tk.Canvas(canvas_frame, width=640, height=480, bg="black")
#         self.canvas.pack(padx=5, pady=5)
#
#         # Status bar
#         status_frame = ttk.Frame(left_frame)
#         status_frame.pack(fill=tk.X, pady=5)
#
#         self.status_label = ttk.Label(status_frame, text="Status: Initializing...", font=("Arial", 10))
#         self.status_label.pack(side=tk.LEFT, padx=5)
#
#         self.landmarks_count_label = ttk.Label(status_frame, text="Landmarks: 0/68", font=("Arial", 10))
#         self.landmarks_count_label.pack(side=tk.RIGHT, padx=5)
#
#         # Right panel - Controls
#         right_frame = ttk.Frame(main_frame)
#         right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
#
#         # Person ID section
#         id_frame = ttk.LabelFrame(right_frame, text="Person Identification")
#         id_frame.pack(fill=tk.X, pady=5)
#
#         ttk.Label(id_frame, text="Person ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
#         self.id_entry = ttk.Entry(id_frame, width=15)
#         self.id_entry.grid(row=0, column=1, padx=5, pady=5)
#         ttk.Button(id_frame, text="Set ID", command=self.set_person_id).grid(row=0, column=2, padx=5, pady=5)
#
#         self.id_label = ttk.Label(id_frame, text="Current ID: None")
#         self.id_label.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="w")
#
#         # Capture options
#         options_frame = ttk.LabelFrame(right_frame, text="Capture Options")
#         options_frame.pack(fill=tk.X, pady=5)
#
#         ttk.Checkbutton(options_frame, text="Show Landmarks", variable=self.show_landmarks).pack(anchor="w", padx=5,
#                                                                                                  pady=2)
#
#         continuous_frame = ttk.Frame(options_frame)
#         continuous_frame.pack(fill=tk.X, padx=5, pady=2)
#         ttk.Checkbutton(continuous_frame, text="Continuous Capture", variable=self.continuous_capture).pack(
#             side=tk.LEFT)
#
#         interval_frame = ttk.Frame(options_frame)
#         interval_frame.pack(fill=tk.X, padx=5, pady=2)
#         ttk.Label(interval_frame, text="Interval (sec):").pack(side=tk.LEFT)
#         interval_spin = ttk.Spinbox(interval_frame, from_=1, to=10, textvariable=self.capture_interval, width=5)
#         interval_spin.pack(side=tk.LEFT, padx=5)
#
#         # Capture buttons
#         capture_frame = ttk.LabelFrame(right_frame, text="Data Collection")
#         capture_frame.pack(fill=tk.X, pady=5)
#
#         ttk.Button(capture_frame, text="Single Capture", command=self.start_capture, style="Accent.TButton").pack(
#             fill=tk.X, padx=5, pady=5)
#         ttk.Button(capture_frame, text="Start Continuous ( every " + str(self.capture_interval.get()) + " sec)", command=self.start_continuous_capture).pack(fill=tk.X,
#                                                                                                        padx=5, pady=5)
#         ttk.Button(capture_frame, text="Stop Continuous", command=self.stop_continuous_capture).pack(fill=tk.X, padx=5,
#                                                                                                      pady=5)
#
#         # Info panel
#         info_frame = ttk.LabelFrame(right_frame, text="Information")
#         info_frame.pack(fill=tk.X, pady=5)
#
#         self.info_text = tk.Text(info_frame, height=8, width=30, wrap=tk.WORD)
#         self.info_text.pack(fill=tk.BOTH, padx=5, pady=5)
#         self.info_text.insert(tk.END, "Welcome to 3D Face Analysis\n\n")
#         self.info_text.insert(tk.END, "1. Set Person ID\n")
#         self.info_text.insert(tk.END, "2. Select capture mode\n")
#         self.info_text.insert(tk.END, "3. Data will be saved to FileObject3D folder\n")
#         self.info_text.config(state=tk.DISABLED)
#
#         # Exit button
#         ttk.Button(right_frame, text="Exit Application", command=self.exit_app).pack(fill=tk.X, pady=10)
#
#         # Apply styles
#         style = ttk.Style()
#         style.configure("Accent.TButton", font=("Arial", 10, "bold"))
#
#     def set_person_id(self):
#         new_id = self.id_entry.get().strip()
#         if not new_id:
#             new_id = simpledialog.askstring("Person ID", "Enter Person ID:", parent=self.root)
#
#         if new_id:
#             self.person_id = new_id
#             self.id_label.config(text=f"Current ID: {self.person_id}")
#
#             # Create person folder
#             person_folder = os.path.join(self.base_folder, self.person_id)
#             if not os.path.exists(person_folder):
#                 os.makedirs(person_folder)
#
#             self.update_info(f"Set ID: {self.person_id}")
#             self.status_label.config(text=f"Status: Ready to capture for {self.person_id}")
#         else:
#             messagebox.showwarning("Missing ID", "Please enter a Person ID")
#
#     def collect_data(self):
#         try:
#             # Get frames from RealSense
#             frames = self.pipeline.wait_for_frames()
#             aligned_frames = self.align.process(frames)
#             color_frame = aligned_frames.get_color_frame()
#             depth_frame = aligned_frames.get_depth_frame()
#
#             if not color_frame or not depth_frame:
#                 self.status_label.config(text="Status: No color/depth frame")
#                 return None, None
#
#             # Convert to numpy arrays
#             color_image = np.asanyarray(color_frame.get_data())
#             depth_image = np.asanyarray(depth_frame.get_data())
#
#             # Create a copy for visualization
#             display_image = color_image.copy()
#
#             # Detect faces using dlib
#             gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
#             faces = self.face_detector(gray_image)
#
#             if not faces:
#                 self.status_label.config(text="Status: No faces detected")
#                 self.landmarks_count_label.config(text="Landmarks: 0/68")
#                 return None, display_image
#
#             # Process the first detected face
#             face = faces[0]
#
#             # Draw face rectangle
#             cv2.rectangle(display_image,
#                           (face.left(), face.top()),
#                           (face.right(), face.bottom()),
#                           (0, 255, 0), 2)
#
#             # Get facial landmarks
#             landmarks = self.landmark_predictor(gray_image, face)
#             landmark_points = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(68)]
#
#             # Draw landmarks on display image if enabled
#             if self.show_landmarks.get():
#                 # Define a unified color for all landmarks (Green: BGR = 0, 255, 0)
#                 unified_color = (0, 255, 0)
#
#                 # Draw all landmark points with the unified color
#                 for group_name, indices in self.landmark_groups.items():
#                     for i in indices:
#                         cv2.circle(display_image, (landmark_points[i][0], landmark_points[i][1]),
#                                    3, unified_color, -1)
#
#             # Get depth information and convert to 3D coordinates
#             depth_scale = self.pipeline.get_active_profile().get_device().first_depth_sensor().get_depth_scale()
#             intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics
#
#             # Collect 3D landmark points
#             landmark_3d = []
#             valid_points = 0
#
#             for x, y in landmark_points:
#                 if 0 <= y < depth_image.shape[0] and 0 <= x < depth_image.shape[1]:
#                     # Get depth value
#                     z = depth_image[y, x]
#
#                     # Check if depth is valid
#                     if z == 0 or z > 10000:  # Invalid depth
#                         # Look for valid depth in surrounding area
#                         z_values = []
#                         for dy in range(-3, 4):
#                             for dx in range(-3, 4):
#                                 nx, ny = x + dx, y + dy
#                                 if 0 <= ny < depth_image.shape[0] and 0 <= nx < depth_image.shape[1]:
#                                     nz = depth_image[ny, nx]
#                                     if nz > 0 and nz < 10000:
#                                         z_values.append(nz)
#
#                         # Use median of valid neighbors
#                         if z_values:
#                             z = np.median(z_values)
#                         else:
#                             landmark_3d.append([0, 0, 0])
#                             continue
#
#                     # Convert to meters and deproject to 3D point
#                     z_meters = z * depth_scale
#                     point_3d = rs.rs2_deproject_pixel_to_point(intrinsics, [x, y], z)
#
#                     # Validate 3D point
#                     if not np.isnan(point_3d).any() and not np.isinf(point_3d).any():
#                         landmark_3d.append(point_3d)
#                         valid_points += 1
#                     else:
#                         landmark_3d.append([0, 0, 0])
#                 else:
#                     landmark_3d.append([0, 0, 0])
#
#             # Update landmarks count label
#             self.landmarks_count_label.config(text=f"Landmarks: {valid_points}/68")
#
#             # Add processing with InsightFace if available
#             face_embedding = None
#             if self.use_insightface:
#                 face_crop = color_image[face.top():face.bottom(), face.left():face.right()]
#                 if face_crop.size > 0:  # Ensure face crop is not empty
#                     faces_insight = self.app.get(face_crop)
#                     if faces_insight:
#                         face_embedding = faces_insight[0].embedding
#
#             return landmark_3d, display_image
#
#         except Exception as e:
#             import traceback
#             traceback.print_exc()
#             self.status_label.config(text=f"Error: {str(e)[:50]}")
#             return None, None
#
#     def start_capture(self):
#         """Capture a single frame of 3D landmarks"""
#         if not self.person_id:
#             messagebox.showwarning("Missing ID", "Please set a Person ID first")
#             return
#
#         self.status_label.config(text="Status: Capturing...")
#         self.root.update()
#
#         # Get landmarks and update display
#         self.landmark_3d, self.display_image = self.collect_data()
#
#         if self.landmark_3d:
#             # Save the data
#             self.save_data()
#             self.status_label.config(text=f"Status: Data captured for {self.person_id}")
#         else:
#             self.status_label.config(text="Status: Failed to capture data")
#
#     def start_continuous_capture(self):
#         """Start continuous capture mode"""
#         if not self.person_id:
#             messagebox.showwarning("Missing ID", "Please set a Person ID first")
#             return
#
#         self.continuous_capture.set(True)
#         self.update_info("Starting continuous capture")
#         self.status_label.config(text=f"Status: Continuous capture for {self.person_id}")
#
#     def stop_continuous_capture(self):
#         """Stop continuous capture mode"""
#         self.continuous_capture.set(False)
#         self.update_info("Stopped continuous capture")
#         self.status_label.config(text="Status: Continuous capture stopped")
#
#     def save_data(self):
#         """Save the captured 3D landmarks to files"""
#         if self.landmark_3d is None or len(self.landmark_3d) == 0:
#             return False
#
#         try:
#             # Create folder structure
#             person_folder = os.path.join(self.base_folder, self.person_id)
#             if not os.path.exists(person_folder):
#                 os.makedirs(person_folder)
#
#             session_folder = os.path.join(person_folder, self.session_id)
#             if not os.path.exists(session_folder):
#                 os.makedirs(session_folder)
#
#             # Save OBJ file
#             timestamp = time.strftime("%H%M%S")
#             obj_file = os.path.join(session_folder, f"{self.person_id}_{self.frame_number}_{timestamp}.obj")
#
#             with open(obj_file, 'w') as f:
#                 f.write('# 3D Face Landmarks\n')
#                 for x_3d, y_3d, z_3d in self.landmark_3d:
#                     f.write(f'v {x_3d} {y_3d} {z_3d}\n')
#
#             # Save metadata JSON
#             meta_file = os.path.join(session_folder, f"{self.person_id}_{self.frame_number}_{timestamp}.json")
#
#             metadata = {
#                 "person_id": self.person_id,
#                 "frame_number": self.frame_number,
#                 "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
#                 "valid_landmarks": sum(1 for p in self.landmark_3d if not (p[0] == 0 and p[1] == 0 and p[2] == 0)),
#                 "total_landmarks": len(self.landmark_3d)
#             }
#
#             with open(meta_file, 'w') as f:
#                 json.dump(metadata, f, indent=2)
#
#             # Increment frame counter
#             self.frame_number += 1
#
#             # Log info
#             self.update_info(f"Saved: Frame {self.frame_number - 1}")
#             return True
#
#         except Exception as e:
#             self.status_label.config(text=f"Error saving data: {str(e)[:50]}")
#             return False
#
#     def update_info(self, message):
#         """Update the info text box"""
#         self.info_text.config(state=tk.NORMAL)
#         self.info_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
#         self.info_text.see(tk.END)
#         self.info_text.config(state=tk.DISABLED)
#
#     def update_video(self):
#         """Update the video feed and process continuous capture"""
#         try:
#             # Process continuous capture if enabled
#             if self.continuous_capture.get() and self.person_id:
#                 current_time = time.time()
#                 if current_time - self.last_capture_time >= self.capture_interval.get():
#                     self.landmark_3d, self.display_image = self.collect_data()
#                     if self.landmark_3d:
#                         if self.save_data():
#                             self.last_capture_time = current_time
#
#             # Regular video update
#             landmark_3d, display_image = self.collect_data()
#
#             if display_image is not None:
#                 # Convert to RGB for PIL
#                 img_rgb = cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB)
#                 img_pil = Image.fromarray(img_rgb)
#                 img_pil = img_pil.resize((640, 480), Image.LANCZOS)
#
#                 # Convert to PhotoImage
#                 self.photo = ImageTk.PhotoImage(img_pil)
#
#                 # Update canvas
#                 self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
#         except Exception as e:
#             self.status_label.config(text=f"Video update error: {str(e)[:50]}")
#
#         # Schedule next update
#         self.root.after(30, self.update_video)  # ~30 FPS
#
#     def exit_app(self):
#         """Safely exit the application"""
#         try:
#             self.pipeline.stop()
#         except:
#             pass
#         self.root.quit()
#         self.root.destroy()
#
#
# if __name__ == "__main__":
#     # Apply a nicer theme if available
#     try:
#         import ttkthemes
#
#         root = ttkthemes.ThemedTk(theme="arc")
#     except:
#         root = tk.Tk()
#
#     app = Face3DAnalysisApp(root)
#     root.mainloop()


import pyrealsense2 as rs
import numpy as np
import cv2
import face_recognition
import pandas as pd
from datetime import datetime
import os
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox


class FaceDataCollector:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Face Data Collector")

        self.pipeline, self.profile, self.depth_scale = self.initialize_realsense()

        self.data = []
        self.current_features = None
        self.current_points_3d = None
        self.label_var = tk.StringVar(value="real")

        self.output_dir = 'face_data'
        self.obj_dir = os.path.join(self.output_dir, 'obj_files')
        os.makedirs(self.obj_dir, exist_ok=True)

        self.setup_gui()

        self.update_video()

    def initialize_realsense(self):
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        profile = pipeline.start(config)
        depth_sensor = profile.get_device().first_depth_sensor()
        depth_scale = depth_sensor.get_depth_scale()
        return pipeline, profile, depth_scale

    def setup_gui(self):
        # Frame cho video
        self.video_label = tk.Label(self.root)
        self.video_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        # Frame cho đặc trưng
        feature_frame = tk.Frame(self.root)
        feature_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # Nhãn hiển thị đặc trưng
        self.nose_depth_label = tk.Label(feature_frame, text="Nose Depth: N/A mm")
        self.nose_depth_label.pack(anchor="w")
        self.avg_eye_depth_label = tk.Label(feature_frame, text="Avg Eye Depth: N/A mm")
        self.avg_eye_depth_label.pack(anchor="w")
        self.face_std_dev_label = tk.Label(feature_frame, text="Face Std Dev: N/A mm")
        self.face_std_dev_label.pack(anchor="w")
        self.nose_eye_diff_label = tk.Label(feature_frame, text="Nose-Eye Diff: N/A mm")
        self.nose_eye_diff_label.pack(anchor="w")

        # Frame cho nhãn
        label_frame = tk.Frame(self.root)
        label_frame.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        tk.Label(label_frame, text="Label:").pack(side=tk.LEFT)
        tk.Radiobutton(label_frame, text="Real", variable=self.label_var, value="real").pack(side=tk.LEFT)
        tk.Radiobutton(label_frame, text="Spoof", variable=self.label_var, value="spoof").pack(side=tk.LEFT)

        # Nút lưu và thoát
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=2, column=1, padx=5, pady=5, sticky="e")

        tk.Button(button_frame, text="Save", command=self.save_data).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Quit", command=self.quit).pack(side=tk.LEFT, padx=5)

    def get_face_landmarks(self, color_image):
        face_locations = face_recognition.face_locations(color_image)
        if not face_locations:
            return None, None
        face_landmarks = face_recognition.face_landmarks(color_image, face_locations)
        if not face_landmarks:
            return None, None
        return face_locations[0], face_landmarks[0]

    def extract_3d_features(self, depth_frame, color_image, face_location, landmarks):
        if face_location is None or landmarks is None:
            return None

        depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
        top, right, bottom, left = face_location

        depth_values = []
        for y in range(top, bottom):
            for x in range(left, right):
                depth = depth_frame.get_distance(x, y)
                if depth > 0:
                    depth_values.append(depth)

        if not depth_values:
            return None

        face_std_dev = np.std(depth_values) / self.depth_scale

        nose_tip = landmarks['nose_tip'][2]
        left_eye = landmarks['left_eye'][0]
        right_eye = landmarks['right_eye'][3]

        nose_depth = depth_frame.get_distance(nose_tip[0], nose_tip[1])
        left_eye_depth = depth_frame.get_distance(left_eye[0], left_eye[1])
        right_eye_depth = depth_frame.get_distance(right_eye[0], right_eye[1])

        if nose_depth == 0 or left_eye_depth == 0 or right_eye_depth == 0:
            return None

        nose_depth /= self.depth_scale
        left_eye_depth /= self.depth_scale
        right_eye_depth /= self.depth_scale
        avg_eye_depth = (left_eye_depth + right_eye_depth) / 2
        nose_eye_diff = nose_depth - avg_eye_depth

        return {
            'nose_depth': nose_depth,
            'avg_eye_depth': avg_eye_depth,
            'face_std_dev': face_std_dev,
            'nose_eye_diff': nose_eye_diff
        }

    def collect_3d_points(self, depth_frame, face_location):
        if face_location is None:
            return None

        top, right, bottom, left = face_location
        depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
        points_3d = []

        for y in range(top, bottom):
            for x in range(left, right):
                depth = depth_frame.get_distance(x, y)
                if depth > 0:
                    point = rs.rs2_deproject_pixel_to_point(depth_intrin, [x, y], depth)
                    points_3d.append(point)

        return points_3d

    def update_video(self):
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        if depth_frame and color_frame:
            color_image = np.asanyarray(color_frame.get_data())
            face_location, landmarks = self.get_face_landmarks(color_image)

            if face_location is not None:
                self.current_features = self.extract_3d_features(depth_frame, color_image, face_location, landmarks)
                self.current_points_3d = self.collect_3d_points(depth_frame, face_location)

                if self.current_features:
                    self.nose_depth_label.config(text=f"Nose Depth: {self.current_features['nose_depth']:.2f} mm")
                    self.avg_eye_depth_label.config(
                        text=f"Avg Eye Depth: {self.current_features['avg_eye_depth']:.2f} mm")
                    self.face_std_dev_label.config(text=f"Face Std Dev: {self.current_features['face_std_dev']:.2f} mm")
                    self.nose_eye_diff_label.config(
                        text=f"Nose-Eye Diff: {self.current_features['nose_eye_diff']:.2f} mm")
                else:
                    self.clear_feature_labels()
            else:
                self.clear_feature_labels()

            # Vẽ khung khuôn mặt
            if face_location:
                top, right, bottom, left = face_location
                cv2.rectangle(color_image, (left, top), (right, bottom), (0, 255, 0), 2)

            # Chuyển đổi khung hình sang định dạng tkinter
            color_image_rgb = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(color_image_rgb)
            image = image.resize((320, 240))  # Giảm kích thước để GUI nhẹ hơn
            photo = ImageTk.PhotoImage(image)
            self.video_label.config(image=photo)
            self.video_label.image = photo

        # Lặp lại cập nhật
        self.root.after(30, self.update_video)

    def clear_feature_labels(self):
        self.nose_depth_label.config(text="Nose Depth: N/A mm")
        self.avg_eye_depth_label.config(text="Avg Eye Depth: N/A mm")
        self.face_std_dev_label.config(text="Face Std Dev: N/A mm")
        self.nose_eye_diff_label.config(text="Nose-Eye Diff: N/A mm")
        self.current_features = None
        self.current_points_3d = None

    def save_data(self):
        if not self.current_features or not self.current_points_3d:
            messagebox.showwarning("Warning", "No face data to save!")
            return

        label = self.label_var.get()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Lưu file .obj
        obj_filename = os.path.join(self.obj_dir, f"face_{timestamp}_{label}.obj")
        with open(obj_filename, 'w') as f:
            for x, y, z in self.current_points_3d:
                f.write(f"v {x:.3f} {y:.3f} {z:.3f}\n")

        # Thêm dữ liệu vào danh sách
        features = self.current_features.copy()
        features['label'] = label
        self.data.append(features)

        # Lưu file CSV
        csv_filename = os.path.join(self.output_dir, f"depth_data_{timestamp}.csv")
        df = pd.DataFrame(self.data)
        df.to_csv(csv_filename, index=False)

        messagebox.showinfo("Success", f"Saved OBJ: {obj_filename}\nSaved CSV: {csv_filename}")

    def quit(self):
        self.pipeline.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = FaceDataCollector(root)
    root.mainloop()
