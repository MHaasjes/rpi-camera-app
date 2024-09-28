import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os
from PIL import Image, ImageTk, ImageOps
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

        # Laat het scherm even wit flitsen om aan te geven dat er een foto is gemaakt
        camera_label.config(bg="white")
        root.update()
        time.sleep(0.5)  # Wacht een halve seconde
        camera_label.config(bg="black")  # Zet achtergrond terug naar zwart
    except Exception as e:
        messagebox.showerror("Fout", f"Kon geen foto maken: {e}")

# Functie om het camerabeeld bij te werken in de GUI
def update_frame():
    frame = picam2.capture_array()

    # Schaal de afbeelding met behoud van de beeldverhouding
    frame_image = Image.fromarray(frame)
    frame_ratio = frame_image.width / frame_image.height
    display_ratio = window_width / window_height

    if frame_ratio > display_ratio:
        # Afbeelding is breder dan het scherm, voeg zwarte balken boven en onder toe
        new_width = window_width
        new_height = int(window_width / frame_ratio)
    else:
        # Afbeelding is hoger dan het scherm, voeg zwarte balken links en rechts toe
        new_height = window_height
        new_width = int(window_height * frame_ratio)

    frame_image = frame_image.resize((new_width, new_height), Image.ANTIALIAS)

    # Maak een zwarte achtergrond om de balken toe te voegen
    frame_image_with_borders = ImageOps.expand(frame_image, (
        (window_width - new_width) // 2,  # Zwarte balk links
        (window_height - new_height) // 2,  # Zwarte balk boven
        (window_width - new_width) // 2,  # Zwarte balk rechts
        (window_height - new_height) // 2  # Zwarte balk onder
    ), fill='black')

    frame_image_tk = ImageTk.PhotoImage(frame_image_with_borders)

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
camera_label = tk.Label(root, bg="black")
camera_label.pack(expand=True, fill=tk.BOTH)

# Rode knop om een foto te maken, zonder tekst
button_frame = tk.Frame(root)
button_frame.pack(pady=10, side=tk.BOTTOM)

button_height = 100  # Schat een hoogte voor de knop om ruimte te reserveren
take_photo_button = tk.Button(button_frame, command=take_photo, bg="red", width=10, height=5)  # Vierkant, zonder tekst
take_photo_button.pack()

# Start de camera en update het beeld in de GUI
update_frame()

# Start de applicatie
root.mainloop()
