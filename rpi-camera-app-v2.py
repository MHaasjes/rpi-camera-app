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
        # Stel de maximale resolutie in voor het maken van de foto
        picam2.stop()  # Stop de preview om de configuratie te kunnen wijzigen
        config_max = picam2.create_still_configuration(main={"size": max_resolution})  # Configureer voor maximale resolutie
        picam2.configure(config_max)
        picam2.start()

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
        
        # Herstart de camera preview
        picam2.stop()  # Stop de foto-configuratie
        picam2.configure(config)  # Herconfigureer naar de oorspronkelijke preview-configuratie
        picam2.start()

    except Exception as e:
        messagebox.showerror("Fout", f"Kon geen foto maken: {e}")

# Functie om video-opname te starten of te stoppen
def toggle_video_recording():
    global recording
    try:
        if not recording:
            # Verander de knop naar rood
            button_canvas.itemconfig(circle, fill="red")

            picam2.stop()  # Stop de preview
            config_video = picam2.create_video_configuration()  # Configureer voor video-opname
            picam2.configure(config_video)
            picam2.start()

            # Start video-opname
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            user = os.getenv("USER")
            save_path = f"/home/{user}/Videos/video_{timestamp}.h264"
            picam2.start_recording(save_path)
            recording = True
        else:
            # Stop video-opname en verander knop terug naar wit
            picam2.stop_recording()
            recording = False
            button_canvas.itemconfig(circle, fill="white")

            # Herstart de preview na de video-opname
            picam2.stop()
            picam2.configure(config)  # Terug naar de oorspronkelijke preview-configuratie
            picam2.start()

    except Exception as e:
        messagebox.showerror("Fout", f"Kon geen video-opname starten: {e}")

# Functie om iconen te wisselen en bijbehorende acties
def switch_icons():
    global current_mode

    if current_mode == "photo":
        # Wissel naar videomodus
        button_canvas.itemconfig(button_symbol, text="▯◄", font=("Helvetica", 10))  # Zet ▯◄ in de cirkel
        video_label.config(text="[O°]", font=("Helvetica", 10), fg="white")  # Zet [O°] rechts van de cirkel
        current_mode = "video"
        button_canvas.bind("<Button-1>", lambda event: toggle_video_recording())  # Bind video-opname functie
    else:
        # Wissel naar fotomodus
        button_canvas.itemconfig(button_symbol, text="[O°]", font=("Helvetica", 10))  # Zet [O°] in de cirkel
        video_label.config(text="▯◄", font=("Helvetica", 10), fg="white")  # Zet ▯◄ rechts van de cirkel
        current_mode = "photo"
        button_canvas.bind("<Button-1>", lambda event: take_photo())  # Bind foto-opname functie

# Functie om het camerabeeld bij te werken in de GUI
def update_frame():
    frame = picam2.capture_array()

    # Schaal de afbeelding met behoud van de beeldverhouding
    frame_image = Image.fromarray(frame)
    frame_ratio = frame_image.width / frame_image.height
    display_ratio = window_width / (window_height - 60)  # Verhouding zonder de zwarte balk

    if (window_width / frame_image.width) < (window_height / frame_image.height):
        new_width = window_width
        new_height = int(new_width / frame_ratio)
    else:
        new_height = window_height - 60
        new_width = int(new_height * frame_ratio)

    frame_image = frame_image.resize((new_width, new_height), Image.ANTIALIAS)

    frame_image_with_borders = ImageOps.expand(frame_image, (
        (window_width - new_width) // 2,
        (window_height - 60 - new_height) // 2,
        (window_width - new_width) // 2,
        (window_height - 60 - new_height) // 2
    ), fill='black')

    frame_image_tk = ImageTk.PhotoImage(frame_image_with_borders)

    camera_label.config(image=frame_image_tk)
    camera_label.image = frame_image_tk
    camera_label.after(10, update_frame)

# Functie om de applicatie netjes af te sluiten
def on_closing():
    try:
        picam2.stop()  # Stop de camera als deze actief is
    except Exception as e:
        print(f"Fout bij het stoppen van de camera: {e}")
    root.destroy()  # Sluit de GUI af

# Start de GUI
root = tk.Tk()
root.title("Raspberry Pi Camera App")

# Voeg een protocol toe om de sluitfunctie te verbinden met de on_closing functie
root.protocol("WM_DELETE_WINDOW", on_closing)

# Haal de schermresolutie op
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Stel het venster in om bijna schermvullend te zijn
window_width = screen_width
window_height = screen_height - 80  # Houd wat ruimte over voor de taakbalk of het menu
root.geometry(f"{window_width}x{window_height}")

# Initialiseer de camera
picam2 = Picamera2()

# Haal de beschikbare sensor modi op en pak de eerste resolutie voor preview
camera_info = picam2.sensor_modes
preview_resolution = camera_info[0]['size']  # Gebruik de eerste resolutie voor de preview

# Configureer de camera voor de preview-resolutie
config = picam2.create_preview_configuration(main={"size": preview_resolution})
picam2.configure(config)
picam2.start()

# Haal de maximale resolutie voor het maken van foto's
max_resolution = max(camera_info, key=lambda mode: mode['size'][0] * mode['size'][1])['size']  # Vind de maximale resolutie

# Camerabeeld label
camera_label = tk.Label(root, bg="black")
camera_label.pack(expand=True, fill=tk.BOTH)

# Zwarte balk onderaan voor de knop (60 pixels hoog)
button_frame = tk.Frame(root, bg="black", height=60)
button_frame.pack(fill=tk.X, side=tk.BOTTOM)

# Frame om de witte cirkel en de videoknop samen te centreren
button_container = tk.Frame(button_frame, bg="black")
button_container.pack(anchor="center")  # Centreer dit frame in het zwarte vlak

# Canvas voor de cirkelvormige knop en symbool
button_canvas = tk.Canvas(button_container, bg="black", width=60, height=60, highlightthickness=0)
button_canvas.grid(row=0, column=0)  # Plaats in grid

# Teken een cirkel op het canvas
circle = button_canvas.create_oval(10, 10, 50, 50, fill="white", outline="")

# Voeg het ASCII-symbool '[O°]' in het midden van de cirkel toe met lettergrootte 10
button_symbol = button_canvas.create_text(30, 30, text="[O°]", fill="black", font=("Helvetica", 10))

# Voeg een klik-event toe aan de cirkel voor het maken van een foto
button_canvas.bind("<Button-1>", lambda event: take_photo())

# Label voor het videomodus-symbool '▯◄', 25 pixels rechts van de cirkel
video_label = tk.Label(button_container, text="▯◄", font=("Helvetica", 10), bg="black", fg="white")
video_label.grid(row=0, column=1, padx=25)  # 25 pixels rechts van de witte knop
video_label.bind("<Button-1>", lambda event: switch_icons())  # Klikbaar om de modus te wisselen

# Resolutie-informatie weergeven in de rechterbovenhoek
resolution_label = tk.Label(root, text=f"Resolutie (preview): {preview_resolution[0]}x{preview_resolution[1]}",
                             bg="black", fg="white", font=("Helvetica", 10))
resolution_label.place(x=10, y=10)  # Plaats het label in de bovenhoek

photo_resolution_label = tk.Label(root, text=f"Resolutie (foto): {max_resolution[0]}x{max_resolution[1]}",
                                   bg="black", fg="white", font=("Helvetica", 10))
photo_resolution_label.place(x=10, y=30)  # Plaats het label iets lager

# Variabelen voor modus en opname-status
current_mode = "photo"
recording = False

# Start de camera en update het beeld in de GUI
update_frame()

# Start de applicatie
root.mainloop()
