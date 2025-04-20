import pyrealsense2 as rs
import numpy as np
import cv2
from insightface.app import FaceAnalysis
import dlib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
import os
import traceback

# --- Configuration ---
DLIB_LANDMARK_MODEL = "shape_predictor_68_face_landmarks.dat"  # Path to dlib's model file
DEBUG_MODE = True  # Set to True for detailed error reporting

# Important landmark indices (based on dlib's 68-point model)
NOSE_TIP_INDEX = 33
LEFT_EYE_INDICES = list(range(36, 42))
RIGHT_EYE_INDICES = list(range(42, 48))


# --- Depth Calculation Functions ---
def calculate_depth_metrics(depth_frame, landmarks, face_bbox):
    """Calculate depth metrics from depth frame and facial landmarks."""
    try:
        depth_image = np.asanyarray(depth_frame.get_data())
        h, w = depth_image.shape

        # Debug: Check if depth data is valid
        if DEBUG_MODE and np.all(depth_image == 0):
            print("Warning: All depth values are zero - check camera alignment")

        landmark_points = [(landmarks.part(n).x, landmarks.part(n).y) for n in range(68)]
        landmark_depths = []
        valid_coords = []

        for i, (x, y) in enumerate(landmark_points):
            if 0 <= x < w and 0 <= y < h:
                depth = depth_image[y, x]
                if depth > 0:
                    landmark_depths.append(depth)
                    valid_coords.append(i)
                else:
                    landmark_depths.append(0)
            else:
                landmark_depths.append(0)

        # Nose depth
        nose_depth = landmark_depths[NOSE_TIP_INDEX] if NOSE_TIP_INDEX in valid_coords else 0

        # Eye depths
        left_eye_depths = [landmark_depths[i] for i in LEFT_EYE_INDICES if i in valid_coords and landmark_depths[i] > 0]
        right_eye_depths = [landmark_depths[i] for i in RIGHT_EYE_INDICES if
                            i in valid_coords and landmark_depths[i] > 0]

        mean_left_eye_depth = np.mean(left_eye_depths) if left_eye_depths else 0
        mean_right_eye_depth = np.mean(right_eye_depths) if right_eye_depths else 0
        avg_eye_depth = (
                                    mean_left_eye_depth + mean_right_eye_depth) / 2 if mean_left_eye_depth > 0 and mean_right_eye_depth > 0 else 0

        # Face region standard deviation
        x1, y1, x2, y2 = face_bbox.astype(int)
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        face_std_dev = 0
        if x1 < x2 and y1 < y2:
            face_region_depth = depth_image[y1:y2, x1:x2]
            valid_face_depths = face_region_depth[face_region_depth > 0]
            if valid_face_depths.size > 10:
                face_std_dev = np.std(valid_face_depths)

        # Nose-eye difference
        nose_eye_diff = avg_eye_depth - nose_depth if avg_eye_depth > 0 and nose_depth > 0 else 0

        if nose_depth > 0 and avg_eye_depth > 0 and face_std_dev > 0:
            return {
                'nose_depth': nose_depth,
                'avg_eye_depth': avg_eye_depth,
                'face_std_dev': face_std_dev,
                'nose_eye_diff': nose_eye_diff
            }
        return None

    except Exception as e:
        if DEBUG_MODE:
            print(f"Error in calculate_depth_metrics: {traceback.format_exc()}")
        return None


# --- Visualization Functions ---
def plot_distributions(df):
    """Plot distributions of collected data."""
    if df.empty:
        print("No data to plot.")
        return

    plt.style.use('seaborn-v0_8-darkgrid')
    plt.figure(figsize=(15, 10))

    # Plot 1: Nose-eye difference
    plt.subplot(2, 2, 1)
    sns.histplot(data=df, x='nose_eye_diff', hue='label', kde=True,
                 palette={'real': 'green', 'spoof': 'red'})
    plt.title('Nose-Eye Depth Difference Distribution (mm)')

    # Plot 2: Face standard deviation
    plt.subplot(2, 2, 2)
    sns.histplot(data=df, x='face_std_dev', hue='label', kde=True,
                 palette={'real': 'green', 'spoof': 'red'})
    plt.title('Face Region Depth Standard Deviation (mm)')

    # Plot 3: Scatter plot
    plt.subplot(2, 2, 3)
    sns.scatterplot(data=df, x='nose_eye_diff', y='face_std_dev', hue='label',
                    palette={'real': 'green', 'spoof': 'red'}, alpha=0.7)
    plt.title('Relationship Between Depth Metrics')

    # Plot 4: Box plot
    plt.subplot(2, 2, 4)
    plot_data = pd.melt(df, id_vars=['label'], value_vars=['nose_eye_diff', 'face_std_dev'],
                        var_name='Metric', value_name='Value')
    sns.boxplot(data=plot_data, x='Metric', y='Value', hue='label',
                palette={'real': 'lightgreen', 'spoof': 'salmon'})
    plt.title('Metric Comparison')

    plt.tight_layout()
    plt.show()


# --- Main Function ---
def main():
    # Initialize RealSense
    print("Initializing RealSense...")
    pipeline = rs.pipeline()
    config = rs.config()

    try:
        # Configure streams
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        profile = pipeline.start(config)

        # Create aligner
        align_to = rs.stream.color
        align = rs.align(align_to)
        print("RealSense initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize RealSense: {traceback.format_exc()}")
        return

    # Initialize InsightFace
    print("Initializing InsightFace...")
    try:
        app = FaceAnalysis(allowed_modules=['detection'],
                           providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
        app.prepare(ctx_id=0, det_size=(640, 640))
        print("InsightFace initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize InsightFace: {traceback.format_exc()}")
        pipeline.stop()
        return

    # Initialize Dlib
    print("Initializing Dlib landmark predictor...")
    try:
        if not os.path.exists(DLIB_LANDMARK_MODEL):
            raise FileNotFoundError(f"Model file not found: {DLIB_LANDMARK_MODEL}")

        landmark_predictor = dlib.shape_predictor(DLIB_LANDMARK_MODEL)

        # Test the predictor
        test_rect = dlib.rectangle(0, 0, 100, 100)
        _ = landmark_predictor(np.zeros((100, 100, 3), dtype=np.uint8), test_rect)
        print("Dlib landmark predictor initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize Dlib: {traceback.format_exc()}")
        pipeline.stop()
        return

    # Main collection loop
    collected_data = []
    window_name = "Face Depth Analysis"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    print("\n=== Data Collection Started ===")
    print("Instructions:")
    print("R - Label as REAL")
    print("S - Label as SPOOF")
    print("N - Skip current face")
    print("Q - Quit and show results")

    try:
        while True:
            # Get frames
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)
            depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()

            if not depth_frame or not color_frame:
                continue

            # Process frames
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            display_image = color_image.copy()

            # Detect faces
            faces = app.get(color_image)
            if DEBUG_MODE and len(faces) > 0:
                print(f"\nDetected {len(faces)} faces")
                for i, face in enumerate(faces):
                    print(f"Face {i}: bbox={face.bbox}, score={face.det_score}")

            # Process each face
            processed_face = False
            for face in faces:
                if processed_face:
                    continue

                bbox = face.bbox.astype(int)
                x1, y1, x2, y2 = bbox

                # Draw initial bounding box
                cv2.rectangle(display_image, (x1, y1), (x2, y2), (0, 255, 255), 2)

                # Get landmarks
                try:
                    dlib_rect = dlib.rectangle(left=x1, top=y1, right=x2, bottom=y2)
                    landmarks = landmark_predictor(color_image, dlib_rect)

                    # Calculate metrics
                    metrics = calculate_depth_metrics(depth_frame, landmarks, face.bbox)

                    if metrics:
                        # Display metrics
                        cv2.putText(display_image, f"StdDev: {metrics['face_std_dev']:.1f}",
                                    (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                        cv2.putText(display_image, f"Nose-Eye: {metrics['nose_eye_diff']:.1f}",
                                    (x1, y2 + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                        cv2.putText(display_image, "Label? (R/S/N/Q)",
                                    (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                        # Wait for user input
                        cv2.imshow(window_name, display_image)
                        key = cv2.waitKey(0) & 0xFF

                        # Process key press
                        if key == ord('r'):
                            metrics['label'] = 'real'
                            collected_data.append(metrics)
                            color = (0, 255, 0)
                            label = "REAL"
                        elif key == ord('s'):
                            metrics['label'] = 'spoof'
                            collected_data.append(metrics)
                            color = (0, 0, 255)
                            label = "SPOOF"
                        elif key == ord('n'):
                            color = (128, 128, 128)
                            label = "SKIPPED"
                        elif key == ord('q'):
                            raise StopIteration
                        else:
                            continue

                        # Update display
                        cv2.rectangle(display_image, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(display_image, label, (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                        cv2.imshow(window_name, display_image)
                        cv2.waitKey(500)

                        processed_face = True

                except Exception as e:
                    if DEBUG_MODE:
                        print(f"Face processing error: {traceback.format_exc()}")
                    cv2.rectangle(display_image, (x1, y1), (x2, y2), (0, 165, 255), 1)
                    cv2.putText(display_image, "Processing Error", (x1, y1 - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 165, 255), 1)
                    processed_face = True

            # Display frame info
            cv2.putText(display_image, f"Collected: {len(collected_data)}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.imshow(window_name, display_image)

            # Check for quit command
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    except StopIteration:
        print("Data collection stopped by user.")
    except Exception as e:
        print(f"Unexpected error: {traceback.format_exc()}")
    finally:
        # Cleanup
        pipeline.stop()
        cv2.destroyAllWindows()

        # Process collected data
        if collected_data:
            df = pd.DataFrame(collected_data)
            print(f"\nCollected {len(df)} samples:")
            print(df.groupby('label').size())

            # Save to CSV
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            csv_file = f"depth_data_{timestamp}.csv"
            df.to_csv(csv_file, index=False)
            print(f"Data saved to {csv_file}")

            # Plot results
            plot_distributions(df)
        else:
            print("\nNo data collected.")


if __name__ == "__main__":
    main()