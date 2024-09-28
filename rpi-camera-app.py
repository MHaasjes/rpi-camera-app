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
    display_ratio = window_width / (window_height - 60)  # Verhouding zonder de zwarte balk

    if frame_ratio > display_ratio:
        # Afbeelding is breder dan het scherm, voeg zwarte balken boven en onder toe
        new_width = window_width
        new_height = int(window_width / frame_ratio)
    else:
        # Afbeelding is hoger dan het scherm, voeg zwarte balken links en rechts toe
        new_height = window_height - 60  # Rekening houden met de balk
        new_width = int(new_height * frame_ratio)

    frame_image = frame_image.resize((new_width, new_height), Image.ANTIALIAS)

    # Maak een zwarte achtergrond om de balken toe te voegen
    frame_image_with_borders = ImageOps.expand(frame_image, (
        (window_width - new_width) // 2,  # Zwarte balk links
        (window_height - 60 - new_height) // 2,  # Zwarte balk boven, zonder de onderste balk
        (window_width - new_width) // 2,  # Zwarte balk rechts
        (window_height - 60 - new_height) // 2  # Zwarte balk onder, zonder de onderste balk
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

# Zwarte balk onderaan voor de knop (60 pixels hoog)
button_frame = tk.Frame(root, bg="black", height=60)
button_frame.pack(fill=tk.X, side=tk.BOTTOM)

# Witte knop (cirkelvormig) in de zwarte balk om een foto te maken
take_photo_button = tk.Button(button_frame, command=take_photo, bg="white", width=3, height=1)
take_photo_button.pack(pady=10)  # Zorg dat de knop netjes in de zwarte balk wordt weergegeven

# Maak de knop cirkelvormig
take_photo_button.configure(height=2)  # Verander de hoogte naar 2 voor cirkelvorm
take_photo_button.bind('<Configure>', lambda e: take_photo_button.config(width=40, height=40))

# Label voor de cameraresolutie
resolution_label = tk.Label(root, text=f"Resolutie: {max_resolution[0]}x{max_resolution[1]}", 
                             bg="black", fg="white", font=("Helvetica", 16))
resolution_label.place(x=10, y=10)  # Plaats het label in de bovenhoek

# Start de camera en update het beeld in de GUI
update_frame()

# Start de applicatie
root.mainloop()
