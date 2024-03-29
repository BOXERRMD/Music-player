import os
import time
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter.messagebox import *


import mutagen.ogg
import vlc
from mutagen.mp3 import MP3
from mutagen import File
from pytube import YouTube


window_youtube = False
window_radio = False

class lecteur_mp3():
    def __init__(self):
        super().__init__()
        self.time_barre_progress = 0
        self.duration_in_seconds = 1
        self.file_path = None
        self.list = []
        self.current_song = 0
        self.show_error = None
        self.player = None
        self.is_playing = False
        self.is_paused = False
        self.root = tk.Tk()
        self.root.title("Music player")
        self.root.iconbitmap("icone.ico")

        self.back_button = tk.Button(self.root, text="Back", foreground="blue", command=self.back_music, font=("font", 10))
        self.pause_resume_button = tk.Button(self.root, text="Pause/Resume", command=self.pause_resume_music, font=("font", 10))
        self.next_button = tk.Button(self.root, text="Next", foreground="blue", command=self.skip_music, font=("font", 10))
        self.pause_resume_button.grid(row=0, column=4, ipadx=20, pady=5, ipady=5)
        self.next_button.grid(row=0, column=5, pady=5, ipadx=10, ipady=5)
        self.back_button.grid(row=0, column=3, pady=5, ipadx=10, ipady=5)


        self.title_musique = tk.Label(self.root, text="Waiting for music...", bg="yellow", anchor="center", font=("font", 12))
        self.title_musique.grid(row=1, column=1, pady=5)

        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_music, foreground="red", font=("font", 10))
        self.stop_button.grid(row=1, column=4, pady=5)

        self.file_button = tk.Button(self.root, text="Select music", relief="solid", foreground="green", command=self.select_file, font=("font", 12))
        self.file_button.grid(pady=5, column=4, ipadx=10, ipady=5)

        self.file_button = tk.Button(self.root, text="Select folder", relief="solid", foreground="purple", command=self.select_folder, font=("font", 12))
        self.file_button.grid(pady=5, column=4, ipadx=10, ipady=5)

        self.volume_scale = tk.Scale(self.root, from_=0, to=100, length=150, orient=tk.HORIZONTAL, label="Volume", command=self.set_volume)
        self.volume_scale.set(100)
        self.volume_scale.grid(row=3, column=1)

        self.repet_music_checkbox = tk.BooleanVar()
        self.repet_music_checkbox.set(False)  # Par défaut, la case n'est pas cochée

        self.show_error_music_checkbox = tk.BooleanVar()
        self.show_error_music_checkbox.set(False)  # Par défaut, la case n'est pas cochée

        self.repet_checkbox = tk.Checkbutton(self.root, text="Repeat", variable=self.repet_music_checkbox)
        self.repet_checkbox.grid(row=5, column=1, sticky="e")

        self.progress_bar = ttk.Progressbar(self.root, orient='horizontal', length=250, mode='determinate')
        self.progress_bar.grid(row=5, column=1, pady=5, padx=5)

        self.temps_musique = tk.Label(self.root, text="", font=("font", 10))
        self.temps_musique.grid(row=5, column=1, sticky="w")

        self.next_title_musique = tk.Label(self.root, text="next song :", bg="lightblue")
        self.next_title_musique.grid(row=2, column=1, pady=5)

        self.liste = tk.Listbox(self.root, height=10, width=50, highlightcolor="purple", highlightbackground="purple",
                           background="#f9ccff", font=("font", 11))
        self.liste.grid(row=7, column=1, pady=5)
        self.liste.bind('<<ListboxSelect>>', self.set_listbox)

        # MENUBAR
        self.menubar = tk.Menu(self.root)

        self.menu1 = tk.Menu(self.menubar, tearoff=0)
        self.menu1.add_command(label="Copyright", command=self.copyright_)
        self.menu1.add_command(label="Help", command=self.help_)
        self.menubar.add_command(label="Error", command=self.show_error_choice)


        self.menu2 = tk.Menu(self.menubar, tearoff=0)
        self.menu2.add_command(label="Download mp3 - mp4", command=self.downloadmp3mp4)
        self.menu2.add_command(label="Radio", command=self.radio)

        self.menubar.add_cascade(label="Info", menu=self.menu1)
        self.menubar.add_cascade(label="Autre", menu=self.menu2)
        self.root.config(menu=self.menubar)

        self.root.bind("<Key>", self.key_press_event)
        lecteur_mp3.update_playlist(self)
        lecteur_mp3.update_progress(self)
        self.root.mainloop()

    def downloadmp3mp4(self):
        global window_youtube
        if not window_youtube:
            DownloadMP3MP4(self.root)
            window_youtube = True
        else:
            showerror(title="Window already open !", message="The window is already open !")

    def radio(self):
        global window_radio
        if not window_radio:
            radio(self.root)
            window_radio = True
        else:
            showerror(title="Window already open !", message="The window is already open !")


    def copyright_(self):
        showinfo("Copyright",
                 f"Copyright (c) 2023 BOXERRMD\n\nAny use of the software as a financial instrument is strictly forbidden. \nAny software-related problems that may damage your computer are not supported by the application or its creator. \nYou can report bugs or security issues on GitHub or Discord: \nhttps://github.com/BOXERRMD/Music-player \nboxer9620")

    def help_(self):
        showinfo("HELP",
                 f"Back: Click once to replay the music. Double-click to play the previous song.\n\npause/resume : Click to pause or resume music.\n\nNext : Click to play the next song.\n\nStop : Stops all music and playback of the selected folder.\n\nRepeat : Check before playing a single song.")

    def show_error_choice(self):
        if not self.show_error:
            if askyesno('Enable error',
                        "If you enable errors, this may cause automatic constraints when switching from song to song. \nThis allows you to see which songs the player doesn't support. "):
                self.show_error = True
                return
        if self.show_error:
            if askyesno('Disable error',
                        "If you deactivate errors, this will smooth out the flow of music, but will not warn you that a song cannot be played. If an error is encountered, it will move on to the next song without saying anything. For simple file playback, it won't play the file without warning you about the problem. "):
                self.show_error = False
                return

    def play_music(self, file_path):

        try:
            audio = MP3(file_path)
            self.duration_in_seconds = audio.info.length

            self.player = vlc.MediaPlayer(file_path)
            self.player.play()
            self.is_playing = True
            self.title_musique.config(
                text=f"{self.current_song + 1} : {self.info_music(file_path)[0]} -\n{self.info_music(file_path)[1]}\n{int(self.duration_in_seconds)} s")  # On modifie l'affichage sur la fenêtre Tkinter

        except vlc.libvlc_errmsg() and mutagen.mp3.HeaderNotFoundError as e:
            if self.show_error:
                self.title_musique.config(text="ERROR")
                showerror('ERROR', str(e))
                self.current_song = self.current_song + 1
            else:
                self.current_song = self.current_song + 1

    def info_music(self, file_path):
        try:
            audio = File(file_path)
            if 'TIT2' in audio:  # Regarde si dans le dictionnaire il y a la clé TIT2
                title = audio['TIT2'][0]  # Récupère le titre de la chanson à partir de la clé
            else:
                title = "Unknown title"  # Sinon il renvoie UNKNOWN
            if 'TPE1' in audio:
                artist = audio['TPE1'][
                    0]  # Récupère l'artist de la chanson à partir de la clé TPE1  (même principe que celui du dessus)
            else:
                artist = "Unknown artist"
            return title, artist
        except:
            title = "ERROR"
            artist = "Unable to read !"
            return title, artist

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Music Files", "*.mp3;*.ogg;*.wave;*.mp4")])
        if self.file_path:
            if self.file_path.endswith(".mp3"):
                self.skip_music()
                self.current_song = 0
                self.reset_listbox()
                self.list = [self.file_path]

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.reset_listbox()
            self.list = []
            for file in os.listdir(folder_path):
                if file.endswith(".mp3"):
                    self.file_path = os.path.join(folder_path, file)
                    self.list.append(self.file_path)
            items = [f"{i + 1} - {self.info_music(self.list[i])[0]} : {self.info_music(self.list[i])[1]}" for i in range(len(self.list))]
            self.liste.insert(tk.END, *items)
            self.skip_music()
            self.current_song = 0

    def pause_resume_music(self):
        if self.player.is_playing():
            self.player.pause()
            self.is_paused = True
            self.progress_bar.stop()
        else:
            self.player.play()
            self.is_paused = False

    def stop_music(self):
        self.player.stop()
        self.progress_bar.stop()
        self.reset_listbox()
        self.list = []
        self.current_song = 0
        self.is_playing = False
        self.title_musique.config(text="Waiting for music...")
        self.next_title_musique.config(text="next song :")

    def skip_music(self):
        if self.repet_music_checkbox.get():
            self.current_song += 1
        if self.player is None:
            pass
        else:
            self.player.stop()
        self.is_playing = False
        self.progress_bar.stop()

    def back_music(self):
        if self.repet_music_checkbox.get():
            pass
        else:
            self.current_song = self.current_song - 1
        self.player.stop()
        self.progress_bar.stop()
        self.is_playing = False

    def set_volume(self, volume):
        self.player.audio_set_volume(int(volume))

    def key_press_event(self, event):
        # Si la touche "+" du pavé numérique est pressée et que le focus est sur la fenêtre principale
        if event.keysym == 'plus' and self.root.focus_get() == self.root:
            current_volume = self.volume_scale.get()
            if current_volume < 100:
                new_volume = min(100, int(current_volume) + 5)  # Augmente le volume par incrément de 5
                self.volume_scale.set(new_volume)
                self.player.audio_set_volume(new_volume)

        # Si la touche "-" du pavé numérique est pressée et que le focus est sur la fenêtre principale
        elif event.keysym == 'minus' and self.root.focus_get() == self.root:
            current_volume = self.volume_scale.get()
            if current_volume > 0:
                new_volume = max(0, int(current_volume) - 5)  # Diminue le volume par incrément de 5
                self.volume_scale.set(new_volume)
                self.player.audio_set_volume(new_volume)



    def set_listbox(self, event):
        self.current_song = self.liste.curselection()[0]
        self.skip_music()

    def reset_listbox(self):
        self.liste.delete(0, len(self.list) - 1)

    def update_progress(self):
        mixer_music_get_pose = 0

        try:
            mixer_music_get_pose = self.player.get_time()
        except:
            pass

        # print("get_pos ", pygame.mixer.music.get_pos())
        # Récupérer la position actuelle de la musique en secondes
        current_time = (mixer_music_get_pose * 100) / self.duration_in_seconds

        # Mettre à jour la barre de progression en fonction de la position actuelle
        self.progress_bar['value'] = current_time / 1000
        # print(progress_bar['value'])

        self.temps_musique.config(text=f"{int(mixer_music_get_pose / 1000)} s")

        # Appeler la fonction update_progress toutes les 1000 millisecondes
        self.root.after(1000, self.update_progress)

    def update_playlist(self):
        if self.is_playing:
            if self.player.is_playing() == 1:
                pass
            else:
                if self.is_paused:
                    pass
                else:
                    self.is_playing = False

        if not self.is_playing:
            if len(self.list) > 0:
                if not self.is_playing:
                    time.sleep(0.5)
                    try:
                        if self.repet_music_checkbox.get():
                            if self.current_song == 0:
                                pass
                            else:
                                self.current_song -= 1
                        self.play_music(self.list[self.current_song])
                        self.next_title_musique.config(
                            text=f"next song : {self.info_music(self.list[self.current_song + 1])[0]} -\n{self.info_music(self.list[self.current_song + 1])[1]}")
                    except:
                        pass
                    if self.current_song > len(self.list):
                        self.stop_music()
                        self.reset_listbox()
                    self.current_song += 1

        self.root.after(1000, self.update_playlist)

# -column, -columnspan, -in, -ipadx, -ipady, -padx, -pady, -row, -rowspan, or -sticky

class DownloadMP3MP4:
    def __init__(self, root):
        self.root2 = tk.Toplevel(root)
        self.root2.title("Music player - downloader YouTube")
        self.root2.iconbitmap("icone.ico")

        self.value = tk.StringVar()
        self.value.set("Put a YouTube link")
        self.entree = tk.Entry(self.root2, width=30, borderwidth=10, textvariable=self.value)
        self.entree.grid(ipadx=30, ipady=20)

        self.bouton_dlmp3 = tk.Button(self.root2, text="Download mp3", command=self.dl_mp3, borderwidth=2, background="yellow", relief="solid")
        self.bouton_dlmp3.grid(sticky="e", row=1, padx=5, pady=5, ipadx=10, ipady=5)

        self.bouton_dlmp4 = tk.Button(self.root2, text="Download mp4", command=self.dl_mp4, borderwidth=2, background="cyan", relief="solid")
        self.bouton_dlmp4.grid(sticky="w", row=1, padx=5, pady=5, ipadx=10, ipady=5)


    def dl_mp3(self):
        if "https" in self.entree.get():
            yt = YouTube(self.entree.get())
            stream = yt.streams.filter(only_audio=True).first()
            stream.download(output_path='Downloaded audio', filename=f"{yt.title}.mp3")
            showinfo("Download", f"Download path : {stream.get_file_path()}")
        else:
            showerror("ERROR", "It's not a valide YouTube link !")

    def dl_mp4(self):
        if "https" in self.entree.get():
            yt = YouTube(self.entree.get())
            stream = yt.streams.filter().first()
            stream.download(output_path='Downloaded video', filename=f"{yt.title}.mp4")
            showinfo("Download", stream.get_file_path())
        else:
            showerror("ERROR", "It's not a valide YouTube link !")



class radio:
    def __init__(self, root):
        self.root3 = tk.Toplevel(root)
        self.root3.title("Music player - Radio")
        self.root3.iconbitmap("icone.ico")
        self.player = None

        self.liste = tk.Listbox(self.root3, height=10, width=50, highlightcolor="purple", highlightbackground="purple",
                                background="#f9ccff", font=("font", 11))
        self.liste.grid(row=1, column=1, pady=5)
        self.liste.bind('<<ListboxSelect>>', self.set_listbox)
        self.radios = {"0": ["Cherie FM", "https://scdn.nrjaudio.fm/fr/30201/mp3_128.mp3?origine=radio.net&cdn_path=adswizz_lbs8&access_token=8397f26ebcd2482aa366024fbf010d12"],
                       "1": ["Nostalgie", "https://scdn.nrjaudio.fm/fr/30601/mp3_128.mp3?origine=radio.net&cdn_path=adswizz_lbs11&access_token=b838a59691984281ab25b55d271d4a24"],
                       "2": ["RTL", "https://streamer-04.rtl.fr/rtl-1-44-128"],
                       "3": ["RTL 2", "https://streamer-03.rtl.fr/rtl2-1-44-128"],
                       "4": ["Europe 1", "https://stream.europe1.fr/europe1.mp3?aw_0_1st.playerid=lgrdrnwsRadiofr"],
                       "5": ["Europe 2", "https://europe2.lmn.fm/europe2.mp3?aw_0_1st.playerid=lgrdnwsRadiofr"],
                       "6": ["NRJ", "https://scdn.nrjaudio.fm/fr/30001/mp3_128.mp3?origine=radio.net&cdn_path=adswizz_lbs10&access_token=22fde58939e043d188b04d382af4f920"],
                       "7": ["SkyRock", "https://icecast.skyrock.net/s/natio_aac_96k"],
                       "8": ["FunRadio", "https://streamer-01.rtl.fr/fun-1-44-128"],
                       "9": ["France Culture", "https://icecast.radiofrance.fr/franceculture-hifi.aac"],
                       "10": ["FranceInfo", "https://icecast.radiofrance.fr/franceinfo-midfi.mp3"]}
        self.liste.insert(tk.END, *[i[0] for i in self.radios.values()])

        self.stop = tk.Button(self.root3, text="Stop radio", foreground="red", font=("font", 10), command=self.stop)
        self.stop.grid(row=2, column=1)

        self.root3.protocol("WM_DELETE_WINDOW", self.fermeture_de_fenetre)


    def set_listbox(self, event):
        try:
            if self.player.is_playing():
                self.player.stop()
        except:
            pass

        self.instance = vlc.Instance("--no-xlib --quiet")
        self.player = self.instance.media_player_new()
        self.media = self.instance.media_new(self.radios[str(self.liste.curselection()[0])][1])
        self.player.set_media(self.media)

        self.player.play()

    def stop(self):
        self.player.stop()
        self.player.exit()

    def fermeture_de_fenetre(self):
        self.player.stop()
        self.root3.destroy()


lecteur_mp3()
