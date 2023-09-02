import os
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter.messagebox import *

import mutagen.ogg
import pygame
from mutagen.mp3 import MP3
from mutagen import File





pygame.mixer.init()
time_barre_progress = 0
duration_in_seconds = 1
file_path = None
list = []
current_song = 0
show_error = None



def copyright_():
    showinfo("Creator", f"BOXER\n\n:D")

def help_():
    showinfo("HELP",
             f"Back: Click once to replay the music. Double-click to play the previous song.\n\npause/resume : Click to pause or resume music.\n\nNext : Click to play the next song.\n\nStop : Stops all music and playback of the selected folder.\n\nRepeat : Check before playing a single song.")


def show_error_choice():
    global show_error
    if not show_error:
        if askyesno('Enable error', "If you enable errors, this may cause automatic constraints when switching from song to song. \nThis allows you to see which songs the player doesn't support. "):
            show_error = True
            return
    if show_error:
        if askyesno('Disable error', "If you deactivate errors, this will smooth out the flow of music, but will not warn you that a song cannot be played. If an error is encountered, it will move on to the next song without saying anything. For simple file playback, it won't play the file without warning you about the problem. "):
            show_error = False
            return




def play_music(file_path):
    global current_song, duration_in_seconds, show_error


    try:
        audio = MP3(file_path)
        duration_in_seconds = audio.info.length

        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        title_musique.config(text=f"{info_music(file_path)[0]} -\n{info_music(file_path)[1]}\n{int(duration_in_seconds)} s")    #On modifie l'affichage sur la fenêtre Tkinter

    except pygame.error and mutagen.mp3.HeaderNotFoundError as e:
        if show_error:
            title_musique.config(text="ERROR")
            showerror('ERROR', str(e))
            current_song = current_song + 1
        else:
            current_song = current_song + 1


def info_music(file_path):
    audio = File(file_path)
    if 'TIT2' in audio:  # Regarde si dans le dictionnaire il y a la clé TIT2
        title = audio['TIT2'][0]  # Récupère le titre de la chanson à partir de la clé
    else:
        title = "Unknown title"  # Sinon il renvoie UNKNOWN
    if 'TPE1' in audio:
        artist = audio['TPE1'][0]  # Récupère l'artist de la chanson à partir de la clé TPE1  (même principe que celui du dessus)
    else:
        artist = "Unknown artist"
    return title, artist




def select_file():
    global file_path, list
    file_path = filedialog.askopenfilename(filetypes=[("Music Files", "*.mp3;*.ogg;*.wave")])
    if file_path:
        if file_path.endswith(".mp3"):
            play_music(file_path)
            list = []


def select_folder():
    global file_path, list, current_song
    list = []
    folder_path = filedialog.askdirectory()
    if folder_path:
        for file in os.listdir(folder_path):
            if file.endswith(".mp3"):
                file_path = os.path.join(folder_path, file)
                list.append(file_path)
        skip_music()
        current_song = 0


def pause_resume_music():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        progress_bar.stop()
    else:
        pygame.mixer.music.unpause()


def stop_music():
    global list, current_song
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    progress_bar.stop()
    list = []
    current_song = 0
    title_musique.config(text="Waiting for music...")
    next_title_musique.config(text="next song :")


def skip_music():
    global current_song
    if repet_music_checkbox.get():
        current_song += 1
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    progress_bar.stop()


def back_music():
    global current_song
    if repet_music_checkbox.get():
        pass
    else:
        current_song = current_song - 1
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    progress_bar.stop()


def set_volume(volume):
    pygame.mixer.music.set_volume(int(volume) / 100)


def update_progress():
    global duration_in_seconds

    mixer_music_get_pos = pygame.mixer.music.get_pos()


    #print("get_pos ", pygame.mixer.music.get_pos())
    # Récupérer la position actuelle de la musique en secondes
    current_time = (mixer_music_get_pos * 100) / duration_in_seconds


    # Mettre à jour la barre de progression en fonction de la position actuelle
    progress_bar['value'] = current_time / 1000
    #print(progress_bar['value'])

    temps_musique.config(text=f"{int(mixer_music_get_pos / 1000)} s")

    # Appeler la fonction update_progress toutes les 1000 millisecondes
    root.after(1000, update_progress)


def update_playlist():
    global current_song, duration_in_seconds
    mixer_music_get_pos = pygame.mixer.music.get_pos()

    if mixer_music_get_pos < 0.5:
        if len(list) > 0:
            try:
                if repet_music_checkbox.get():
                    if current_song == 0:
                        pass
                    else:
                        current_song -= 1
                play_music(list[current_song])
                next_title_musique.config(text=f"next song : {info_music(list[current_song + 1])[0]} -\n{info_music(list[current_song + 1])[1]}")
            except:
                pass
            current_song += 1
    root.after(1000, update_playlist)





root = tk.Tk()
root.title("Music player")


back_button = tk.Button(root, text="Back", foreground="blue", command=back_music)
pause_resume_button = tk.Button(root, text="Pause/Resume", command=pause_resume_music)
next_button = tk.Button(root, text="Next", foreground="blue", command=skip_music)



title_musique = tk.Label(root, text="Waiting for music...", bg="yellow")
title_musique.grid(row=1, column=0, pady=5)


pause_resume_button.grid(row=0, column=3, ipadx=20, pady=5)
next_button.grid(row=0, column=4, pady=5)
back_button.grid(row=0, column=2, pady=5)






stop_button = tk.Button(root, text="Stop", command=stop_music, foreground="red")
stop_button.grid(row=1, column=3, pady=5)





file_button = tk.Button(root, text="Select music", relief="groove", foreground="green", command=select_file)
file_button.grid(pady=5, column=3)





file_button = tk.Button(root, text="Select folder", relief="groove", foreground="orange", command=select_folder)
file_button.grid(pady=5, column=3)




volume_scale = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, label="Volume", command=set_volume)
volume_scale.set(100)
volume_scale.grid(row=2, column=0)





repet_music_checkbox = tk.BooleanVar()
repet_music_checkbox.set(False)  # Par défaut, la case n'est pas cochée

show_error_music_checkbox = tk.BooleanVar()
show_error_music_checkbox.set(False)  # Par défaut, la case n'est pas cochée



repet_checkbox = tk.Checkbutton(root, text="Repeat", variable=repet_music_checkbox)
repet_checkbox.grid(row=3,column=0)




progress_bar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
progress_bar.grid(row=5, column=0, pady=5, padx=5)


temps_musique = tk.Label(root, text="")
temps_musique.grid(row=5, column=1)



next_title_musique = tk.Label(root, text="next song :")
next_title_musique.grid(row=6, column=0, pady=5)



#MENUBAR
menubar = tk.Menu(root)

menu1 = tk.Menu(menubar, tearoff=0)
menu1.add_command(label="Copyright", command=copyright_)
menu1.add_command(label="Help", command=help_)
menubar.add_command(label="Error", command=show_error_choice)

menubar.add_cascade(label="Info", menu=menu1)
root.config(menu=menubar)







update_playlist()
update_progress()
pygame.init()
root.mainloop()


