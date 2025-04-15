import cv2
import numpy as np
import pyrealsense2 as rs
import mediapipe as mp

pipeline = rs.pipeline()
config = rs.config()

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

pipeline.start(config)

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

while True:
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()

    if not depth_frame or not color_frame:
        continue

    depth_image = np.asanyarray(depth_frame.get_data())
    color_image = np.asanyarray(color_frame.get_data())

    rgb_frame = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for landmarks in results.multi_face_landmarks:
            mp_drawing.draw_landmarks(
                image=color_image,
                landmark_list=landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)
            )

            nose_x, nose_y = int(landmarks.landmark[1].x * color_image.shape[1]), int(landmarks.landmark[1].y * color_image.shape[0])
            left_eye_x, left_eye_y = int(landmarks.landmark[33].x * color_image.shape[1]), int(landmarks.landmark[33].y * color_image.shape[0])
            right_eye_x, right_eye_y = int(landmarks.landmark[133].x * color_image.shape[1]), int(landmarks.landmark[133].y * color_image.shape[0])
            chin_x, chin_y = int(landmarks.landmark[152].x * color_image.shape[1]), int(landmarks.landmark[152].y * color_image.shape[0])

            nose_x = np.clip(nose_x, 0, color_image.shape[1] - 1)
            nose_y = np.clip(nose_y, 0, color_image.shape[0] - 1)
            left_eye_x = np.clip(left_eye_x, 0, color_image.shape[1] - 1)
            left_eye_y = np.clip(left_eye_y, 0, color_image.shape[0] - 1)
            right_eye_x = np.clip(right_eye_x, 0, color_image.shape[1] - 1)
            right_eye_y = np.clip(right_eye_y, 0, color_image.shape[0] - 1)
            chin_x = np.clip(chin_x, 0, color_image.shape[1] - 1)
            chin_y = np.clip(chin_y, 0, color_image.shape[0] - 1)

            depth_nose = depth_image[nose_y, nose_x]
            depth_left_eye = depth_image[left_eye_y, left_eye_x]
            depth_right_eye = depth_image[right_eye_y, right_eye_x]
            depth_chin = depth_image[chin_y, chin_x]

            depth_diff_left = abs(depth_nose - depth_left_eye)
            depth_diff_right = abs(depth_nose - depth_right_eye)
            depth_diff_chin = abs(depth_nose - depth_chin)

            if (depth_diff_left < 40 and depth_diff_right < 40) or depth_diff_chin < 40:
                cv2.putText(color_image, "Possible spoofing attempt", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 0, 255), 2)
            else:
                cv2.putText(color_image, "Live face detected", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Anti-Spoofing with RealSense Depth", color_image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

pipeline.stop()
cv2.destroyAllWindows()