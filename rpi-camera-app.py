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

    # Schaal de afbeelding zodat het binnen het venster past zonder de beeldverhouding te verstoren
    frame_image = Image.fromarray(frame)
    frame_image = frame_image.resize((window_width, window_height), Image.ANTIALIAS)
    frame_image_tk = ImageTk.PhotoImage(frame_image)

    camera_label.config(image=frame_image_tk)
    camera_label.image = frame_image_tk
    camera_label.after(10, update_frame)

# Start de GUI
root = tk.Tk()
root.title("Raspberry Pi Camera App")

# Haal de schermresolutie op
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Stel het venster in om bijna schermvullend te zijn (ruimte laten voor de taakbalk en menu's)
window_width = screen_width
window_height = screen_height - 80  # Houd wat ruimte over voor de taakbalk of het menu
root.geometry(f"{window_width}x{window_height}")

# Initialiseer de camera
picam2 = Picamera2()

# Haal de maximale resolutie van de camera op
camera_info = picam2.sensor_modes
max_resolution = camera_info[0]['size']  # De maximale resolutie wordt opgehaald uit de beschikbare modi

# Configureer de camera voor maximale resolutie
config = picam2.create_preview_configuration(main={"size": max_resolution})
picam2.configure(config)
picam2.start()

# Camerabeeld label
camera_label = tk.Label(root)
camera_label.pack(expand=True)

# Vierkante rode knop om een foto te maken, zonder tekst
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

take_photo_button = tk.Button(button_frame, command=take_photo, bg="red", width=10, height=5)  # Vierkant, zonder tekst
take_photo_button.pack()

# Start de camera en update het beeld in de GUI
update_frame()

# Start de applicatie
root.mainloop()
