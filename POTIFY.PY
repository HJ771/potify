import flet as ft
import pygame
import os
import asyncio
from pathlib import Path
from mutagen.mp3 import MP3

pygame.mixer.init()

def main(page: ft.Page):
    page.title = "Potify - Music Player"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.window_width = 400
    page.window_height = 750
    page.window_resizable = False

    uploaded_songs = []
    playlist_songs = []
    current_song_index = None
    song_duration = 0
    is_playing = False

    title = ft.Text("Potify", size=40, color="#BB86FC", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)

    uploaded_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nombre del Archivo", color="white")),
        ],
        rows=[],
        bgcolor="#1E1E1E",
        border=ft.border.all(1, "#BB86FC")
    )

    playlist_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nombre del Archivo", color="white")),
        ],
        rows=[],
        bgcolor="#1E1E1E",
        border=ft.border.all(1, "#BB86FC")
    )

    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            uploaded_table.rows.clear()
            for file in e.files:
                uploaded_songs.append(file.path)
                uploaded_table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(Path(file.path).name, color="white"))]))
            page.update()

    def pick_folder_result(e: ft.FilePickerResultEvent):
        if e.path:
            playlist_table.rows.clear()
            for file in os.listdir(e.path):
                if file.endswith(".mp3"):
                    full_path = os.path.join(e.path, file)
                    playlist_songs.append(full_path)
                    playlist_table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(file, color="white"))]))
            page.update()

    file_picker = ft.FilePicker(on_result=pick_files_result)
    folder_picker = ft.FilePicker(on_result=pick_folder_result)
    page.overlay.extend([file_picker, folder_picker])

    def get_song_duration(file_path):
        try:
            audio = MP3(file_path)
            return int(audio.info.length)
        except:
            return 0

    def play_song(index, song_list):
        nonlocal current_song_index, song_duration, is_playing
        if 0 <= index < len(song_list):
            current_song_index = index
            pygame.mixer.music.load(song_list[index])
            song_duration = get_song_duration(song_list[index])
            if song_duration == 0:
                return
            pygame.mixer.music.play()
            is_playing = True
            status_text.value = f"Reproduciendo: {Path(song_list[index]).name}"
            page.update()

    def toggle_pause(e):
        nonlocal is_playing
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            is_playing = False
            status_text.value = "Pausado"
        else:
            pygame.mixer.music.unpause()
            is_playing = True
        page.update()

    def stop_song(e):
        pygame.mixer.music.stop()
        is_playing = False
        status_text.value = "Detenido"
        page.update()

    upload_button = ft.ElevatedButton("Subir Música", icon=ft.icons.UPLOAD_FILE, on_click=lambda _: file_picker.pick_files(allow_multiple=True))
    folder_button = ft.ElevatedButton("Subir Carpeta", icon=ft.icons.FOLDER_OPEN, on_click=lambda _: folder_picker.get_directory_path())
    
    play_button = ft.IconButton(icon=ft.icons.PLAY_ARROW, on_click=lambda _: play_song(0, uploaded_songs))
    pause_button = ft.IconButton(icon=ft.icons.PAUSE, on_click=toggle_pause)
    stop_button = ft.IconButton(icon=ft.icons.STOP, on_click=stop_song)

    status_text = ft.Text("Sin reproducción", color="white", size=14)

    page.add(
        ft.Column([
            title,
            ft.Row([upload_button, folder_button], alignment=ft.MainAxisAlignment.CENTER),
            ft.Text("Canciones Individuales", color="white", size=16, weight=ft.FontWeight.BOLD),
            uploaded_table,
            ft.Text("Playlist", color="white", size=16, weight=ft.FontWeight.BOLD),
            playlist_table,
            ft.Row([play_button, pause_button, stop_button], alignment=ft.MainAxisAlignment.CENTER),
            status_text
        ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
    )

ft.app(target=main)
