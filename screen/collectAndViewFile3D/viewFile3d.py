import matplotlib

matplotlib.use('TkAgg')  # Use Tkinter backend
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class Face3DViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Face Landmarks Viewer")
        self.root.geometry("1000x800")

        # Frame for controls
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Buttons
        tk.Button(self.control_frame, text="Load OBJ File 1", command=self.load_file1).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Load OBJ File 2", command=self.load_file2).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Compare Files", command=self.compare_files).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Reset View", command=self.reset_view).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Save Figure", command=self.save_figure).pack(side=tk.LEFT, padx=5)

        # Display options
        self.view_frame = tk.Frame(self.control_frame)
        self.view_frame.pack(side=tk.RIGHT, padx=10)

        # Checkboxes for landmark groups
        self.show_jaw = tk.BooleanVar(value=True)
        self.show_eyebrows = tk.BooleanVar(value=True)
        self.show_nose = tk.BooleanVar(value=True)
        self.show_eyes = tk.BooleanVar(value=True)
        self.show_mouth = tk.BooleanVar(value=True)

        tk.Checkbutton(self.view_frame, text="Jaw", variable=self.show_jaw, command=self.update_display).pack(
            side=tk.LEFT)
        tk.Checkbutton(self.view_frame, text="Eyebrows", variable=self.show_eyebrows, command=self.update_display).pack(
            side=tk.LEFT)
        tk.Checkbutton(self.view_frame, text="Nose", variable=self.show_nose, command=self.update_display).pack(
            side=tk.LEFT)
        tk.Checkbutton(self.view_frame, text="Eyes", variable=self.show_eyes, command=self.update_display).pack(
            side=tk.LEFT)
        tk.Checkbutton(self.view_frame, text="Mouth", variable=self.show_mouth, command=self.update_display).pack(
            side=tk.LEFT)

        # Stats frame
        self.stats_frame = tk.Frame(root)
        self.stats_frame.pack(side=tk.TOP, fill=tk.X, padx=10)

        self.stats_label = tk.Label(self.stats_frame, text="No data loaded", font=("Arial", 10))
        self.stats_label.pack(side=tk.LEFT, padx=5)

        # Figure for plotting
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')

        # Embed plot in tkinter
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Add toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.canvas_frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Data storage
        self.landmarks1 = None
        self.landmarks2 = None
        self.file1_name = None
        self.file2_name = None

        # Define landmark groups
        self.jaw_indices = list(range(0, 17))
        self.eyebrows_indices = list(range(17, 27))
        self.nose_indices = list(range(27, 36))
        self.eyes_indices = list(range(36, 48))
        self.mouth_indices = list(range(48, 68))

    def read_obj_vertices(self, obj_file):
        vertices = []
        try:
            with open(obj_file, 'r') as f:
                for line in f:
                    if line.startswith('v '):  # Vertex line
                        parts = line.strip().split()
                        x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                        vertices.append([x, y, z])
            return vertices
        except FileNotFoundError:
            messagebox.showerror("Error", f"File {obj_file} not found.")
            return []
        except Exception as e:
            messagebox.showerror("Error", f"Error reading {obj_file}: {e}")
            return []

    def load_file1(self):
        filename = filedialog.askopenfilename(filetypes=[("OBJ files", "*.obj")])
        if filename:
            self.landmarks1 = self.read_obj_vertices(filename)
            self.file1_name = filename.split('/')[-1]
            if self.landmarks1:
                messagebox.showinfo("Success", f"Loaded {len(self.landmarks1)} vertices from {self.file1_name}")
                self.update_display()

    def load_file2(self):
        filename = filedialog.askopenfilename(filetypes=[("OBJ files", "*.obj")])
        if filename:
            self.landmarks2 = self.read_obj_vertices(filename)
            self.file2_name = filename.split('/')[-1]
            if self.landmarks2:
                messagebox.showinfo("Success", f"Loaded {len(self.landmarks2)} vertices from {self.file2_name}")
                self.update_display()

    def compare_files(self):
        if not self.landmarks1 or not self.landmarks2:
            messagebox.showwarning("Warning", "Please load both files first")
            return

        if len(self.landmarks1) != len(self.landmarks2):
            messagebox.showwarning("Warning",
                                   f"Files have different numbers of vertices: {len(self.landmarks1)} vs {len(self.landmarks2)}")

        # Calculate differences
        diffs = []
        for i in range(min(len(self.landmarks1), len(self.landmarks2))):
            v1 = self.landmarks1[i]
            v2 = self.landmarks2[i]
            # Skip zeros (missing data)
            if (v1[0] == 0 and v1[1] == 0 and v1[2] == 0) or (v2[0] == 0 and v2[1] == 0 and v2[2] == 0):
                continue
            diff = np.sqrt((v2[0] - v1[0]) ** 2 + (v2[1] - v1[1]) ** 2 + (v2[2] - v1[2]) ** 2)
            diffs.append(diff)

        if diffs:
            avg_diff = np.mean(diffs)
            max_diff = np.max(diffs)
            min_diff = np.min(diffs)
            std_diff = np.std(diffs)

            stats_text = f"Stats: Avg diff: {avg_diff:.4f}m, Max: {max_diff:.4f}m, Min: {min_diff:.4f}m, StdDev: {std_diff:.4f}m"
            self.stats_label.config(text=stats_text)
        else:
            self.stats_label.config(text="No valid points for comparison")

    def update_display(self):
        self.ax.clear()

        if self.landmarks1:
            self.plot_landmarks(self.landmarks1, 'blue', 'o', self.file1_name or "File 1")

        if self.landmarks2:
            self.plot_landmarks(self.landmarks2, 'red', '^', self.file2_name or "File 2")

        # Setup axes
        self.ax.set_xlabel('X (m)')
        self.ax.set_ylabel('Y (m)')
        self.ax.set_zlabel('Z (m)')
        self.ax.set_title('3D Face Landmarks Comparison')

        # Add legend if we have data
        if self.landmarks1 or self.landmarks2:
            self.ax.legend()

        # Make axes equal
        self.set_axes_equal(self.ax)

        # Draw connections between landmarks
        if self.landmarks1 and len(self.landmarks1) >= 68:
            self.draw_connections(self.landmarks1, 'blue')

        if self.landmarks2 and len(self.landmarks2) >= 68:
            self.draw_connections(self.landmarks2, 'red')

        self.canvas.draw()

    def plot_landmarks(self, landmarks, color, marker, label):
        # Filter landmarks by group
        if len(landmarks) >= 68:  # Has enough points for landmark groups
            # Convert to numpy for easier manipulation
            landmarks_np = np.array(landmarks)

            # Plot jaw
            if self.show_jaw.get():
                jaw_pts = landmarks_np[self.jaw_indices]
                valid_pts = jaw_pts[~np.all(jaw_pts == 0, axis=1)]
                if len(valid_pts) > 0:
                    self.ax.scatter(valid_pts[:, 0], valid_pts[:, 1], valid_pts[:, 2],
                                    c=color, marker=marker, label=f"{label} (Jaw)")

            # Plot eyebrows
            if self.show_eyebrows.get():
                brow_pts = landmarks_np[self.eyebrows_indices]
                valid_pts = brow_pts[~np.all(brow_pts == 0, axis=1)]
                if len(valid_pts) > 0:
                    self.ax.scatter(valid_pts[:, 0], valid_pts[:, 1], valid_pts[:, 2],
                                    c=color, marker=marker)

            # Plot nose
            if self.show_nose.get():
                nose_pts = landmarks_np[self.nose_indices]
                valid_pts = nose_pts[~np.all(nose_pts == 0, axis=1)]
                if len(valid_pts) > 0:
                    self.ax.scatter(valid_pts[:, 0], valid_pts[:, 1], valid_pts[:, 2],
                                    c=color, marker=marker)

            # Plot eyes
            if self.show_eyes.get():
                eyes_pts = landmarks_np[self.eyes_indices]
                valid_pts = eyes_pts[~np.all(eyes_pts == 0, axis=1)]
                if len(valid_pts) > 0:
                    self.ax.scatter(valid_pts[:, 0], valid_pts[:, 1], valid_pts[:, 2],
                                    c=color, marker=marker)

            # Plot mouth
            if self.show_mouth.get():
                mouth_pts = landmarks_np[self.mouth_indices]
                valid_pts = mouth_pts[~np.all(mouth_pts == 0, axis=1)]
                if len(valid_pts) > 0:
                    self.ax.scatter(valid_pts[:, 0], valid_pts[:, 1], valid_pts[:, 2],
                                    c=color, marker=marker)
        else:
            # Just plot everything if we can't identify groups
            x = [v[0] for v in landmarks if not (v[0] == 0 and v[1] == 0 and v[2] == 0)]
            y = [v[1] for v in landmarks if not (v[0] == 0 and v[1] == 0 and v[2] == 0)]
            z = [v[2] for v in landmarks if not (v[0] == 0 and v[1] == 0 and v[2] == 0)]
            if x and y and z:
                self.ax.scatter(x, y, z, c=color, marker=marker, label=label)

    def draw_connections(self, landmarks, color):
        """Draw lines connecting landmarks in meaningful ways"""
        # Only draw if we have valid points
        landmarks_np = np.array(landmarks)

        # Draw jaw line
        if self.show_jaw.get():
            self.draw_line_between_points(landmarks_np, self.jaw_indices, color)

        # Draw eyebrows
        if self.show_eyebrows.get():
            self.draw_line_between_points(landmarks_np, range(17, 22), color)  # Left eyebrow
            self.draw_line_between_points(landmarks_np, range(22, 27), color)  # Right eyebrow

        # Draw nose
        if self.show_nose.get():
            self.draw_line_between_points(landmarks_np, range(27, 31), color)  # Nose bridge
            self.draw_line_between_points(landmarks_np, [30, 31, 32, 33, 34, 35, 30], color)  # Nose base

        # Draw eyes
        if self.show_eyes.get():
            self.draw_line_between_points(landmarks_np, [36, 37, 38, 39, 40, 41, 36], color)  # Left eye
            self.draw_line_between_points(landmarks_np, [42, 43, 44, 45, 46, 47, 42], color)  # Right eye

        # Draw mouth
        if self.show_mouth.get():
            self.draw_line_between_points(landmarks_np, [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 48],
                                          color)  # Outer lips
            self.draw_line_between_points(landmarks_np, [60, 61, 62, 63, 64, 65, 66, 67, 60], color)  # Inner lips

    def draw_line_between_points(self, landmarks_np, indices, color):
        """Draw a line connecting points with given indices"""
        points = landmarks_np[indices]
        # Filter out points with all zeros
        valid_points = []

        for point in points:
            if not (point[0] == 0 and point[1] == 0 and point[2] == 0):
                valid_points.append(point)

        if len(valid_points) > 1:
            valid_points = np.array(valid_points)
            self.ax.plot(valid_points[:, 0], valid_points[:, 1], valid_points[:, 2],
                         color=color, linewidth=1, alpha=0.6)

    def set_axes_equal(self, ax):
        """Set 3D plot axes to equal scale"""
        x_limits = ax.get_xlim3d()
        y_limits = ax.get_ylim3d()
        z_limits = ax.get_zlim3d()

        x_range = abs(x_limits[1] - x_limits[0])
        x_middle = np.mean(x_limits)
        y_range = abs(y_limits[1] - y_limits[0])
        y_middle = np.mean(y_limits)
        z_range = abs(z_limits[1] - z_limits[0])
        z_middle = np.mean(z_limits)

        # Set the plot box dimensions to be equal
        max_range = 0.5 * max([x_range, y_range, z_range])
        ax.set_xlim3d([x_middle - max_range, x_middle + max_range])
        ax.set_ylim3d([y_middle - max_range, y_middle + max_range])
        ax.set_zlim3d([z_middle - max_range, z_middle + max_range])

    def reset_view(self):
        """Reset the 3D view to default angles"""
        self.ax.view_init(elev=30, azim=45)
        self.canvas.draw()

    def save_figure(self):
        """Save the current figure to a file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("PDF files", "*.pdf")]
        )
        if filename:
            self.fig.savefig(filename, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Success", f"Figure saved to {filename}")


if __name__ == "__main__":
    root = tk.Tk()
    app = Face3DViewer(root)
    root.mainloop()