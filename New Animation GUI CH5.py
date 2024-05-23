import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import cv2
from PIL import Image, ImageTk

class ProstheticSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Prosthetic Leg Simulator")

        # Variables
        self.activity = tk.StringVar(value="Walking")
        self.activities = ["Walking", "Running", "Jumping", "Standing"]
        self.pressure_data = np.random.normal(50, 10, 1000)  # Example pressure data for walking
        self.max_voltage = 24.0
        self.max_current = 10.0
        self.current_frame = 0
        self.cap = None

        # UI Elements
        self.create_widgets()
        self.update_data()

    def create_widgets(self):
        # Activity selection
        ttk.Label(self.root, text="Activity:").pack()
        activity_menu = ttk.OptionMenu(self.root, self.activity, "Walking", *self.activities, command=self.update_activity)
        activity_menu.pack()

        # Pressure Graph
        self.fig, self.ax = plt.subplots()
        self.ax.set_title("Pressure Sensor Reading")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Pressure (kPa)")
        self.line, = self.ax.plot([], [], lw=2)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack()

        # Motor Torque Display
        self.torque_display = ttk.Label(self.root, text="Motor Torque: 0 Nm")
        self.torque_display.pack()

        # Color Indicator Ball
        self.ball_canvas = tk.Canvas(self.root, width=50, height=50)
        self.ball_canvas.pack()
        self.ball = self.ball_canvas.create_oval(10, 10, 40, 40, fill="green")

        # Animation Canvas
        self.animation_canvas = tk.Canvas(self.root, width=400, height=200)
        self.animation_canvas.pack()

        # Animation
        self.animation = animation.FuncAnimation(self.fig, self.animate_graph, frames=100, interval=100, blit=True)

        # Video Frame
        self.video_frame = tk.Label(self.root)
        self.video_frame.pack()

    def update_activity(self, event):
        if self.activity.get() == "Walking":
            self.pressure_data = np.random.normal(50, 10, 1000)  # Walking data
            self.load_video("walking.mp4")
        elif self.activity.get() == "Running":
            self.pressure_data = np.random.normal(70, 15, 1000)  # Running data
            self.load_video("running.mp4")
        elif self.activity.get() == "Jumping":
            self.pressure_data = np.random.normal(80, 20, 1000)  # Jumping data
            self.load_video("jumping.mp4")
        elif self.activity.get() == "Standing":
            self.pressure_data = np.random.normal(30, 5, 1000)  # Standing data
            self.load_video("standing.mp4")
        self.update_data()

    def load_video(self, video_path):
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(video_path)
        self.play_video()

    def play_video(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_frame.imgtk = imgtk
            self.video_frame.config(image=imgtk)
            self.video_frame.after(20, self.play_video)
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def update_data(self):
        self.xdata = np.arange(0, len(self.pressure_data))
        self.ydata = self.pressure_data
        self.line.set_data(self.xdata, self.ydata)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
        self.update_motor_torque()

    def calculate_motor_torque(self, pressure):
        # Simplified linear mapping for demonstration
        voltage = self.max_voltage * (pressure / 100)
        current = self.max_current * (pressure / 100)
        torque = voltage * current  # Simplified calculation
        return torque

    def update_motor_torque(self):
        pressure = self.pressure_data[self.current_frame % len(self.pressure_data)]
        torque = self.calculate_motor_torque(pressure)
        self.torque_display.config(text=f"Motor Torque: {torque:.2f} Nm")
        self.update_color_indicator(torque)

    def update_color_indicator(self, torque):
        if torque < 50:
            color = "green"
        elif torque < 100:
            color = "yellow"
        else:
            color = "red"
        self.ball_canvas.itemconfig(self.ball, fill=color)

    def animate_graph(self, frame):
        self.current_frame = frame
        self.line.set_ydata(np.roll(self.pressure_data, -frame))
        self.update_motor_torque()
        return self.line,

if __name__ == "__main__":
    root = tk.Tk()
    app = ProstheticSimulator(root)
    root.mainloop()
