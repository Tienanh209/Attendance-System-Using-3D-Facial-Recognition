import os
import numpy as np
import cv2
import pyrealsense2 as rs
import dlib
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class DepthCollectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Depth Data Collection")
        self.root.geometry("1000x650")
        self.root.configure(bg="#B3E5FC")  # Light sea blue background

        # Initialize data directory
        self.data_dir = "../../assets/AntiSpoofing_DT"
        os.makedirs(self.data_dir, exist_ok=True)

        # Set up RealSense camera
        self.pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.profile = self.pipeline.start(config)
        self.align = rs.align(rs.stream.color)

        # Load dlib models
        self.face_detector = dlib.get_frontal_face_detector()
        self.landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

        # Define landmark indices
        self.nose_tip_index = 33
        self.left_eye_indices = list(range(36, 42))
        self.right_eye_indices = list(range(42, 48))
        self.jaw_indices = list(range(0, 17))

        # Initialize GUI
        self.create_widgets()

        # Start video display
        self.show_frame()

    def create_widgets(self):
        # Back button
        self.btn_back = tk.Button(self.root, text="Back", font=("Arial", 12, "bold"),
                                  bg="#4699A6", fg="white", width=10, height=2, borderwidth=0,
                                  command=self.close_app)
        self.btn_back.place(x=30, y=20)

        # Header
        self.header_label = tk.Label(self.root, text="Depth Data Collection", font=("Arial", 24, "bold"),
                                     bg="#B3E5FC", fg="black")
        self.header_label.place(relx=0.5, y=40, anchor="center")

        # Video frame
        self.video_frame = tk.Frame(self.root, width=640, height=400, bg="white", relief="solid",
                                    borderwidth=2, highlightbackground="#8A2BE2", highlightthickness=3)
        self.video_frame.place(x=60, y=100)

        self.video_label = tk.Label(self.video_frame, text="Camera display frame", font=("Arial", 18, "bold"),
                                    bg="white")
        self.video_label.place(relx=0.5, rely=0.5, anchor="center")

        # Save data button
        self.btn_save = tk.Button(self.root, text="Save", font=("Arial", 14, "bold"),
                                  bg="#4699A6", fg="white", width=10, height=2, borderwidth=0,
                                  command=self.capture_and_save_data)
        self.btn_save.place(x=800, y=280)

        # Status label
        self.status_label = tk.Label(self.root, text="📷 Please face the camera",
                                     font=("Arial", 12), fg="black", bg="#B3E5FC")
        self.status_label.place(relx=0.5, rely=0.95, anchor="center")

    def process_frame(self):
        """Capture and align color and depth frames from RealSense camera"""
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()

        if not color_frame or not depth_frame:
            return None, None

        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        return color_image, depth_image

    def detect_faces_3d(self, color_image, depth_image):
        """Detect faces and compute depth metrics"""
        faces = self.face_detector(color_image)
        results = []

        for face in faces:
            # Convert to dlib rectangle
            dlib_rect = face

            # Get landmarks
            landmarks = self.landmark_predictor(color_image, dlib_rect)
            landmark_points = [(landmarks.part(n).x, landmarks.part(n).y) for n in range(68)]

            # Get depth values for landmarks
            landmark_depths = []
            for x, y in landmark_points:
                if 0 <= x < depth_image.shape[1] and 0 <= y < depth_image.shape[0]:
                    depth = depth_image[y, x]
                    landmark_depths.append(depth)
                else:
                    landmark_depths.append(0)

            # Validate depth data
            valid_depths = [d for d in landmark_depths if d > 0]
            if len(valid_depths) < 0.5 * len(landmark_depths):
                self.status_label.config(text="⚠️ Invalid depth data!", fg="red")
                continue

            # Compute specific depth metrics
            nose_depth = landmark_depths[self.nose_tip_index]
            mean_left_eye_depth = np.mean([landmark_depths[i] for i in self.left_eye_indices if landmark_depths[i] > 0])
            mean_right_eye_depth = np.mean([landmark_depths[i] for i in self.right_eye_indices if landmark_depths[i] > 0])
            mean_jaw_depth = np.mean([landmark_depths[i] for i in self.jaw_indices if landmark_depths[i] > 0])

            # Calculate average eye depth
            avg_eye_depth = (mean_left_eye_depth + mean_right_eye_depth) / 2 if (mean_left_eye_depth and mean_right_eye_depth) else 0

            # Compute depth differences
            nose_eye_diff = nose_depth - avg_eye_depth if avg_eye_depth > 0 else 0
            jaw_eye_diff = mean_jaw_depth - avg_eye_depth if avg_eye_depth > 0 else 0

            # Calculate standard deviation of face region
            face_region_depth = depth_image[face.top():face.bottom(), face.left():face.right()]
            std_dev = np.std(face_region_depth) if face_region_depth.size > 0 else 0

            results.append({
                'landmark_points': np.array(landmark_points),
                'landmark_depths': np.array(landmark_depths),
                'nose_eye_diff': nose_eye_diff,
                'jaw_eye_diff': jaw_eye_diff,
                'std_dev': std_dev,
                'nose_depth': nose_depth,
                'mean_left_eye_depth': mean_left_eye_depth,
                'mean_right_eye_depth': mean_right_eye_depth,
                'mean_jaw_depth': mean_jaw_depth,
                'avg_eye_depth': avg_eye_depth
            })

        return results

    def show_frame(self):
        """Display video feed with face detection and landmarks"""
        color_image, depth_image = self.process_frame()
        if color_image is None or depth_image is None:
            self.video_label.after(10, self.show_frame)
            return

        face_results = self.detect_faces_3d(color_image, depth_image)

        for result in face_results:
            # Draw bounding box (approximate from landmarks)
            x_coords, y_coords = zip(*result['landmark_points'])
            x_min, x_max = int(min(x_coords)), int(max(x_coords))
            y_min, y_max = int(min(y_coords)), int(max(y_coords))
            cv2.rectangle(color_image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            cv2.putText(color_image, "Face Detected", (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # Draw landmarks
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
        """Capture and save depth data"""
        color_image, depth_image = self.process_frame()
        if color_image is None or depth_image is None:
            messagebox.showerror("❌ Error", "Could not capture image from camera!")
            return

        face_results = self.detect_faces_3d(color_image, depth_image)

        if not face_results:
            self.status_label.config(text="❌ No face detected!", fg="red")
            messagebox.showerror("❌ Error", "No face detected, please try again!")
            return

        result = face_results[0]  # Take the first detected face

        # Generate unique file name
        data_count = len(os.listdir(self.data_dir)) + 1
        data_path = os.path.join(self.data_dir, f"antispoof_{data_count}.npy")

        # Prepare data to save
        data_to_save = {
            'landmark_points': result['landmark_points'],
            'landmark_depths': result['landmark_depths'],
            'nose_eye_diff': result['nose_eye_diff'],
            'jaw_eye_diff': result['jaw_eye_diff'],
            'std_dev': result['std_dev'],
            'nose_depth': result['nose_depth'],
            'mean_left_eye_depth': result['mean_left_eye_depth'],
            'mean_right_eye_depth': result['mean_right_eye_depth'],
            'mean_jaw_depth': result['mean_jaw_depth'],
            'avg_eye_depth': result['avg_eye_depth']
        }

        np.save(data_path, data_to_save)
        self.status_label.config(text="✅ Data saved!", fg="green")
        messagebox.showinfo("✅ Success", f"Saved depth data to antispoof_{data_count}.npy")

    def close_app(self):
        """Clean up and close the application"""
        self.pipeline.stop()
        cv2.destroyAllWindows()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = DepthCollectionApp(root)
    root.mainloop()