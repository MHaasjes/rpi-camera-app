import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os
from PIL import Image, ImageTk, ImageOps
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
import time

def configure_camera(mode="preview"):
    """Configureer de camera op basis van de modus."""
    if mode == "preview":
        config = picam2.create_preview_configuration(main={"size": preview_resolution})
    elif mode == "photo":
        config = picam2.create_still_configuration(main={"size": max_resolution})
    else:  # video
        config = picam2.create_video_configuration()
    
    picam2.configure(config)
    picam2.start()

def take_photo():
    """Neem een foto en sla deze op."""
    try:
        picam2.stop()  # Stop de preview voor configuratie
        configure_camera(mode="photo")  # Configureer voor foto
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        save_path = f"/home/{os.getenv('USER')}/Pictures/photo_{timestamp}.jpg"
        picam2.capture_file(save_path)
        flash_feedback()
        configure_camera(mode="preview")  # Terug naar preview
    except Exception as e:
        messagebox.showerror("Fout", f"Kon geen foto maken: {e}")

def flash_feedback():
    """Geef visuele feedback na het maken van een foto."""
    camera_label.config(bg="white")
    root.update()
    time.sleep(0.5)
    camera_label.config(bg="black")

def toggle_video_recording():
    """Start of stop video-opname."""
    global recording
    try:
        if not recording:
            button_canvas.itemconfig(circle, fill="red")
            configure_camera(mode="video")  # Configureer voor video-opname
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            save_path = f"/home/{os.getenv('USER')}/Videos/video_{timestamp}.h264"
            encoder = H264Encoder(bitrate=10000000)  # H264 encoder met bitrate
            picam2.start_recording(encoder, save_path)
            recording = True
        else:
            picam2.stop_recording()
            recording = False
            button_canvas.itemconfig(circle, fill="white")
            configure_camera(mode="preview")  # Terug naar preview
    except Exception as e:
        messagebox.showerror("Fout", f"Kon geen video-opname starten: {e}")

def switch_icons():
    """Wissel tussen foto- en videomodus."""
    global current_mode
    if current_mode == "photo":
        current_mode = "video"
        button_canvas.itemconfig(button_symbol, text="▯◄")
        video_label.config(text="[O°]")
        button_canvas.bind("<Button-1>", lambda event: toggle_video_recording())
    else:
        current_mode = "photo"
        button_canvas.itemconfig(button_symbol, text="[O°]")
        video_label.config(text="▯◄")
        button_canvas.bind("<Button-1>", lambda event: take_photo())

def update_frame():
    """Update het camerabeeld in de GUI."""
    frame = picam2.capture_array()
    frame_image = Image.fromarray(frame)
    
    # Schaal de afbeelding met behoud van de aspectverhouding
    frame_image.thumbnail((window_width, window_height - 60), Image.ANTIALIAS)
    frame_image_with_borders = ImageOps.expand(frame_image, (
        (window_width - frame_image.width) // 2,
        (window_height - 60 - frame_image.height) // 2,
        (window_width - frame_image.width) // 2,
        (window_height - 60 - frame_image.height) // 2
    ), fill='black')

    camera_label.image = ImageTk.PhotoImage(frame_image_with_borders)
    camera_label.config(image=camera_label.image)
    camera_label.after(10, update_frame)

def on_closing():
    """Sluit de applicatie netjes af."""
    try:
        picam2.stop()
    except Exception as e:
        print(f"Fout bij het stoppen van de camera: {e}")
    root.destroy()

# Start de GUI
root = tk.Tk()
root.title("Raspberry Pi Camera App")
root.protocol("WM_DELETE_WINDOW", on_closing)

# Haal de schermresolutie op
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_height = screen_height - 80
root.geometry(f"{screen_width}x{window_height}")

# Initialiseer de camera
picam2 = Picamera2()
camera_info = picam2.sensor_modes
preview_resolution = camera_info[0]['size']
max_resolution = max(camera_info, key=lambda mode: mode['size'][0] * mode['size'][1])['size']

configure_camera()  # Start met preview-configuratie

# Camerabeeld label
camera_label = tk.Label(root, bg="black")
camera_label.pack(expand=True, fill=tk.BOTH)

# Knoppenframe
button_frame = tk.Frame(root, bg="black", height=60)
button_frame.pack(fill=tk.X, side=tk.BOTTOM)

# Canvas voor de cirkelvormige knop
button_canvas = tk.Canvas(button_frame, bg="black", width=60, height=60, highlightthickness=0)
button_canvas.pack(side=tk.LEFT, padx=(screen_width // 2 - 30, 0))  # Centreer de knop

# Teken een cirkel op het canvas
circle = button_canvas.create_oval(10, 10, 50, 50, fill="white")

# Voeg het ASCII-symbool '[O°]' in het midden van de cirkel toe
button_symbol = button_canvas.create_text(30, 30, text="[O°]", font=("Helvetica", 10))

# Label voor het tweede symbool ▯◄
video_label = tk.Label(button_frame, text="▯◄", bg="black", fg="white", font=("Helvetica", 10))
video_label.pack(side=tk.LEFT, padx=25)
video_label.bind("<Button-1>", lambda event: switch_icons())

# Resolutielabel
resolution_label = tk.Label(root, text=f"Resolutie (preview): {preview_resolution[0]}x{preview_resolution[1]}", 
                             bg="black", fg="white", font=("Helvetica", 10))
resolution_label.place(x=10, y=10)

# Start de frame-updater
update_frame()

# Zet de huidige modus op 'photo' en de opname-status op False
current_mode = "photo"
recording = False

# Start de GUI
root.mainloop()

# Stop de camera bij het afsluiten
picam2.stop()
