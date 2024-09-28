import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os
from PIL import Image, ImageTk
from picamera2 import Picamera2
import time

# Functie om foto te maken
def take_photo():
    try:
        # Maak een foto met de camera
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        user = os.getenv("USER")  # Haal de ingelogde gebruiker op
        save_path = f"/home/{user}/Pictures/photo_{timestamp}.jpg"

        picam2.capture_file(save_path)
        messagebox.showinfo("Foto", f"Foto opgeslagen als: {save_path}")

    except Exception as e:
        messagebox.showerror("Fout", f"Kon geen foto maken: {e}")

# Functie om het camerabeeld bij te werken in de GUI
def update_frame():
    frame = picam2.capture_array()
    frame_image = ImageTk.PhotoImage(Image.fromarray(frame))
    camera_label.config(image=frame_image)
    camera_label.image = frame_image
    camera_label.after(10, update_frame)

# Start de GUI
root = tk.Tk()
root.title("Raspberry Pi Camera App")

# Initialiseer de camera
picam2 = Picamera2()

# Haal de maximale resolutie van de camera op
camera_info = picam2.sensor_modes
max_resolution = camera_info[0]['size']  # De maximale resolutie wordt opgehaald uit de beschikbare modi

# Configureer de camera voor maximale resolutie
config = picam2.create_preview_configuration(main={"size": max_resolution})
picam2.configure(config)
picam2.start()

# Camerabeeld label met grotere preview (2x zo groot)
camera_label = tk.Label(root, width=max_resolution[0]//2, height=max_resolution[1]//2)
camera_label.pack()

# Rode knop om een foto te maken
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

take_photo_button = tk.Button(button_frame, text="Neem Foto", command=take_photo, bg="red", fg="white", font=("Arial", 20), width=10, height=2)
take_photo_button.pack()

# Start de camera en update het beeld in de GUI
update_frame()

# Start de applicatie
root.mainloop()
