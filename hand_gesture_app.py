#!/usr/bin/env python3
"""
🤖 AI-Powered Hand Gesture Recognition App
==========================================
A modern computer vision application that uses your webcam to detect hand gestures
and perform interactive actions with a beautiful UI.

Features:
- Real-time hand detection and tracking
- Gesture recognition (peace sign, thumbs up, fist, etc.)
- Virtual mouse control
- Interactive UI with modern styling
- Multiple gesture modes
"""

import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import time
import pyautogui
import math
from collections import deque

class HandGestureApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 AI Hand Gesture Recognition")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Camera setup
        self.cap = None
        self.is_running = False
        self.current_frame = None
        
        # Gesture recognition
        self.gesture_history = deque(maxlen=10)
        self.last_gesture_time = 0
        self.gesture_cooldown = 1.0  # seconds
        
        # Virtual mouse settings
        self.mouse_mode = False
        self.screen_width, self.screen_height = pyautogui.size()
        
        # UI variables
        self.gesture_label = tk.StringVar(value="No gesture detected")
        self.confidence_label = tk.StringVar(value="Confidence: 0%")
        self.fps_label = tk.StringVar(value="FPS: 0")
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        
        self.setup_ui()
        self.setup_styles()
        
    def setup_styles(self):
        """Setup modern UI styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', 
                       font=('Arial', 16, 'bold'),
                       foreground='#00ff88',
                       background='#1a1a1a')
        
        style.configure('Info.TLabel',
                       font=('Arial', 12),
                       foreground='#ffffff',
                       background='#1a1a1a')
        
        style.configure('Status.TLabel',
                       font=('Arial', 10),
                       foreground='#ffaa00',
                       background='#1a1a1a')
        
        style.configure('Modern.TButton',
                       font=('Arial', 11, 'bold'),
                       padding=(10, 5))
        
        style.map('Modern.TButton',
                 background=[('active', '#00ff88'),
                           ('pressed', '#00cc66')])
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main title
        title_frame = tk.Frame(self.root, bg='#1a1a1a')
        title_frame.pack(pady=20)
        
        title_label = ttk.Label(title_frame, 
                               text="🤖 AI Hand Gesture Recognition",
                               style='Title.TLabel')
        title_label.pack()
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(expand=True, fill='both', padx=20)
        
        # Left panel - Camera feed
        left_panel = tk.Frame(main_frame, bg='#2a2a2a', relief='raised', bd=2)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Camera label
        self.camera_label = tk.Label(left_panel, 
                                   text="📹 Camera Feed",
                                   font=('Arial', 14, 'bold'),
                                   fg='#00ff88',
                                   bg='#2a2a2a')
        self.camera_label.pack(pady=10)
        
        # Video display
        self.video_frame = tk.Frame(left_panel, bg='#000000', relief='sunken', bd=2)
        self.video_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        self.video_label = tk.Label(self.video_frame, bg='#000000')
        self.video_label.pack(expand=True, fill='both')
        
        # Right panel - Controls and info
        right_panel = tk.Frame(main_frame, bg='#2a2a2a', relief='raised', bd=2)
        right_panel.pack(side='right', fill='y', padx=(10, 0))
        right_panel.configure(width=300)
        
        # Control buttons
        control_frame = tk.Frame(right_panel, bg='#2a2a2a')
        control_frame.pack(pady=20, padx=20, fill='x')
        
        self.start_btn = ttk.Button(control_frame, 
                                  text="🚀 Start Camera",
                                  command=self.start_camera,
                                  style='Modern.TButton')
        self.start_btn.pack(fill='x', pady=5)
        
        self.stop_btn = ttk.Button(control_frame,
                                 text="⏹️ Stop Camera",
                                 command=self.stop_camera,
                                 style='Modern.TButton',
                                 state='disabled')
        self.stop_btn.pack(fill='x', pady=5)
        
        # Gesture info
        info_frame = tk.Frame(right_panel, bg='#2a2a2a')
        info_frame.pack(pady=20, padx=20, fill='x')
        
        ttk.Label(info_frame, text="🎯 Current Gesture:", style='Info.TLabel').pack(anchor='w')
        self.gesture_display = ttk.Label(info_frame, 
                                        textvariable=self.gesture_label,
                                        style='Status.TLabel')
        self.gesture_display.pack(anchor='w', pady=5)
        
        ttk.Label(info_frame, text="📊 Confidence:", style='Info.TLabel').pack(anchor='w', pady=(10, 0))
        self.confidence_display = ttk.Label(info_frame,
                                           textvariable=self.confidence_label,
                                           style='Status.TLabel')
        self.confidence_display.pack(anchor='w', pady=5)
        
        ttk.Label(info_frame, text="⚡ Performance:", style='Info.TLabel').pack(anchor='w', pady=(10, 0))
        self.fps_display = ttk.Label(info_frame,
                                    textvariable=self.fps_label,
                                    style='Status.TLabel')
        self.fps_display.pack(anchor='w', pady=5)
        
        # Gesture modes
        mode_frame = tk.Frame(right_panel, bg='#2a2a2a')
        mode_frame.pack(pady=20, padx=20, fill='x')
        
        ttk.Label(mode_frame, text="🎮 Gesture Modes:", style='Info.TLabel').pack(anchor='w')
        
        self.mouse_mode_var = tk.BooleanVar()
        mouse_check = ttk.Checkbutton(mode_frame,
                                    text="🖱️ Virtual Mouse Control",
                                    variable=self.mouse_mode_var,
                                    command=self.toggle_mouse_mode)
        mouse_check.pack(anchor='w', pady=5)
        
        # Gesture list
        gesture_frame = tk.Frame(right_panel, bg='#2a2a2a')
        gesture_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        ttk.Label(gesture_frame, text="✋ Supported Gestures:", style='Info.TLabel').pack(anchor='w')
        
        gestures_text = """
👋 Open Hand - Wave gesture
✌️ Peace Sign - Two fingers up
👍 Thumbs Up - Thumb up
👊 Fist - Closed hand
👈 Point - Index finger
✋ Stop - Open palm
        """
        
        gesture_info = tk.Text(gesture_frame, 
                             height=8, 
                             width=25,
                             bg='#1a1a1a',
                             fg='#ffffff',
                             font=('Consolas', 9),
                             relief='flat',
                             bd=0)
        gesture_info.pack(fill='both', expand=True, pady=5)
        gesture_info.insert('1.0', gestures_text)
        gesture_info.config(state='disabled')
    
    def start_camera(self):
        """Start the camera and begin processing"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Could not open camera!")
                return
            
            self.is_running = True
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            
            # Start the camera thread
            self.camera_thread = threading.Thread(target=self.camera_loop, daemon=True)
            self.camera_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start camera: {str(e)}")
    
    def stop_camera(self):
        """Stop the camera and processing"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.gesture_label.set("No gesture detected")
        self.confidence_label.set("Confidence: 0%")
    
    def toggle_mouse_mode(self):
        """Toggle virtual mouse control mode"""
        self.mouse_mode = self.mouse_mode_var.get()
        if self.mouse_mode:
            messagebox.showinfo("Mouse Mode", "Virtual mouse control enabled!\nUse your index finger to control the cursor.")
    
    def camera_loop(self):
        """Main camera processing loop"""
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Process frame for hand detection
            processed_frame = self.process_frame(frame)
            
            # Update UI
            self.update_video_display(processed_frame)
            self.update_fps()
    
    def process_frame(self, frame):
        """Process frame for hand detection and gesture recognition"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        results = self.hands.process(rgb_frame)
        
        # Draw hand landmarks and detect gestures
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 255, 136), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(0, 255, 136), thickness=2)
                )
                
                # Detect gesture
                gesture, confidence = self.detect_gesture(hand_landmarks)
                
                # Update gesture info
                if gesture != "Unknown" and time.time() - self.last_gesture_time > self.gesture_cooldown:
                    self.gesture_label.set(f"🎯 {gesture}")
                    self.confidence_label.set(f"Confidence: {confidence:.1f}%")
                    self.last_gesture_time = time.time()
                    
                    # Handle gesture actions
                    self.handle_gesture_action(gesture, hand_landmarks)
        
        return frame
    
    def detect_gesture(self, landmarks):
        """Detect hand gesture from landmarks"""
        # Get landmark positions
        points = []
        for landmark in landmarks.landmark:
            points.append([landmark.x, landmark.y, landmark.z])
        
        points = np.array(points)
        
        # Calculate finger states
        finger_states = self.get_finger_states(points)
        
        # Gesture recognition logic
        gesture, confidence = self.classify_gesture(finger_states, points)
        
        return gesture, confidence
    
    def get_finger_states(self, points):
        """Determine which fingers are extended"""
        # Finger tip indices
        tip_ids = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        
        finger_states = []
        
        # Thumb (special case)
        thumb_up = points[4][1] < points[3][1]
        finger_states.append(thumb_up)
        
        # Other fingers
        for i in range(1, 5):
            finger_up = points[tip_ids[i]][1] < points[tip_ids[i] - 2][1]
            finger_states.append(finger_up)
        
        return finger_states
    
    def classify_gesture(self, finger_states, points):
        """Classify gesture based on finger states"""
        thumb, index, middle, ring, pinky = finger_states
        
        # Gesture patterns
        if all(finger_states):  # All fingers up
            return "Open Hand", 90.0
        elif not any(finger_states):  # All fingers down
            return "Fist", 85.0
        elif index and middle and not ring and not pinky and not thumb:
            return "Peace Sign", 88.0
        elif thumb and not index and not middle and not ring and not pinky:
            return "Thumbs Up", 92.0
        elif index and not middle and not ring and not pinky and not thumb:
            return "Point", 87.0
        elif not thumb and not index and not middle and not ring and not pinky:
            return "Stop", 90.0
        else:
            return "Unknown", 0.0
    
    def handle_gesture_action(self, gesture, landmarks):
        """Handle actions based on detected gestures"""
        if not self.mouse_mode:
            return
        
        # Get index finger position for mouse control
        if gesture == "Point":
            index_tip = landmarks.landmark[8]
            x = int(index_tip.x * self.screen_width)
            y = int(index_tip.y * self.screen_height)
            
            # Move mouse cursor
            pyautogui.moveTo(x, y, duration=0.1)
        
        # Add more gesture actions here
        if gesture == "Thumbs Up":
            # Could trigger a click or other action
            pass
    
    def update_video_display(self, frame):
        """Update the video display in the UI"""
        # Resize frame to fit display
        height, width = frame.shape[:2]
        max_width, max_height = 640, 480
        
        # Calculate scaling
        scale = min(max_width/width, max_height/height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Resize frame
        frame_resized = cv2.resize(frame, (new_width, new_height))
        
        # Convert to PhotoImage
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)
        photo = ImageTk.PhotoImage(image)
        
        # Update label
        self.video_label.configure(image=photo)
        self.video_label.image = photo  # Keep a reference
    
    def update_fps(self):
        """Update FPS counter"""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.fps_start_time >= 1.0:
            fps = self.fps_counter / (current_time - self.fps_start_time)
            self.fps_label.set(f"FPS: {fps:.1f}")
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.stop_camera()
        finally:
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()

def main():
    """Main function to run the application"""
    print("🤖 Starting AI Hand Gesture Recognition App...")
    print("📋 Make sure your webcam is connected and working!")
    print("🎯 Supported gestures: Open Hand, Peace Sign, Thumbs Up, Fist, Point, Stop")
    print("🖱️ Enable Virtual Mouse Control to control your cursor with gestures!")
    
    app = HandGestureApp()
    app.run()

if __name__ == "__main__":
    main()
