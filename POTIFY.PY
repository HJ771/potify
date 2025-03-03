import flet as ft
import pygame
from pathlib import Path
from mutagen.mp3 import MP3
import asyncio
import os
import sqlite3
import pyperclip

pygame.mixer.init()

def main(page: ft.Page):
    page.title = "Potify- Music Player"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.window_width = 400
    page.window_height = 750
    page.window_resizable = False
    page.scroll = ft.ScrollMode.AUTO

    uploaded_songs = []
    current_playlist = []  
    current_song_index = None
    song_duration = 0
    is_playing = False

    title = ft.Text("Potify", size=40, color="#BB86FC",
                   weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)

    uploaded_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nombre del Archivo", color="white")),
            ft.DataColumn(ft.Text("Acción", color="white")),
        ],
        rows=[],
        bgcolor="#1E1E1E",
        border=ft.border.all(1, "#BB86FC"),
        column_spacing=20,
    )

    file_picker = ft.FilePicker(on_result=lambda e: pick_files_result(e))
    page.overlay.append(file_picker)

    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            uploaded_table.rows.clear()
            uploaded_songs.clear()
            for index, file in enumerate(e.files):
                uploaded_songs.append(file.path)
                uploaded_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(Path(file.path).name, color="white")),
                            ft.DataCell(
                                ft.Row([
                                    ft.IconButton(
                                        icon=ft.Icons.PLAY_ARROW,
                                        on_click=lambda _, idx=index: play_song(idx, uploaded_songs),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.CONTENT_COPY,
                                        on_click=lambda _, path=file.path: copy_song_path(path),
                                    ),
                                ], spacing=5)
                            ),
                        ]
                    )
                )
            page.update()

    progress_slider = ft.Slider(min=0, max=100, value=0, disabled=True)
    progress_text = ft.Text("00:00 / 00:00", color="white", size=12)
    status_text = ft.Text("Sin reproducción", color="white", size=14)

    async def update_progress():
        while is_playing and current_song_index is not None:
            try:
                position = pygame.mixer.music.get_pos() / 1000
                if position >= song_duration:
                    next_index = current_song_index + 1
                    if next_index < len(current_playlist):
                        play_song(next_index, current_playlist)
                    else:
                        stop_song(None)
                        break
                progress_slider.value = position
                progress_text.value = f"{format_time(position)} / {format_time(song_duration)}"
                page.update()
            except Exception as e:
                print(f"Error en barra de tiempo: {e}")
            await asyncio.sleep(0.5)

    def play_song(index, song_list):
        nonlocal current_song_index, song_duration, is_playing, current_playlist
        if 0 <= index < len(song_list):
            current_playlist = song_list
            current_song_index = index
            pygame.mixer.music.load(song_list[index])
            song_duration = get_song_duration(song_list[index])
            progress_slider.max = song_duration
            progress_slider.value = 0
            pygame.mixer.music.play()
            is_playing = True
            page.run_task(update_progress)
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
            page.run_task(update_progress)
            status_text.value = f"Reproduciendo: {Path(current_playlist[current_song_index]).name}"
        page.update()

    def stop_song(e):
        nonlocal is_playing
        pygame.mixer.music.stop()
        is_playing = False
        progress_slider.value = 0
        progress_text.value = "00:00 / 00:00"
        status_text.value = "Detenido"
        page.update()

    upload_button = ft.ElevatedButton(
        "Subir Música",
        icon=ft.Icons.UPLOAD_FILE,
        on_click=lambda _: file_picker.pick_files(allow_multiple=True),
        bgcolor="#BB86FC",
        color="#121212",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    play_button = ft.IconButton(
        icon=ft.Icons.PLAY_ARROW,
        on_click=lambda _: play_song(current_song_index or 0, current_playlist or uploaded_songs)
    )
    pause_button = ft.IconButton(icon=ft.Icons.PAUSE, on_click=toggle_pause)
    stop_button = ft.IconButton(icon=ft.Icons.STOP, on_click=stop_song)

    def create_playlist(name):
        conn = sqlite3.connect("playlists.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO playlists(name) VALUES(?)", (name,))
        conn.commit()
        conn.close()

    def add_song_to_playlist(playlist_id, song_path):
        conn = sqlite3.connect("playlists.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO playlist_songs(playlist_id, song_path) VALUES(?, ?)",
                      (playlist_id, song_path))
        conn.commit()
        conn.close()

    def play_playlist():
        conn = sqlite3.connect("playlists.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM playlists")
        playlists = cursor.fetchall()
        conn.close()

        if not playlists:
            return

        try:
            playlist_id = int(input("ID de la playlist: "))
            conn = sqlite3.connect("playlists.db")
            cursor = conn.cursor()
            cursor.execute("SELECT song_path FROM playlist_songs WHERE playlist_id=?", (playlist_id,))
            songs = [row[0] for row in cursor.fetchall()]
            conn.close()

            if not songs:
                return

            current_playlist = songs
            play_song(0, current_playlist)
        except ValueError:
            pass

    def manage_playlists():
        while True:
            choice = input("Seleccione una opción: ").strip()

            if choice == "1":
                name = input("Nombre de la playlist: ").strip()
                if name:
                    create_playlist(name)
            elif choice == "2":
                play_playlist()
            elif choice == "3":
                break

    manage_playlist_button = ft.ElevatedButton(
        "Gestionar Playlists (Consola)",
        icon=ft.Icons.LIBRARY_MUSIC,
        on_click=lambda _: page.run_thread(manage_playlists),
        bgcolor="#BB86FC",
        color="#121212",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    page.add(
        ft.Column([
            ft.Container(title, alignment=ft.alignment.center, margin=ft.margin.only(top=20, bottom=20)),
            ft.Row([upload_button, manage_playlist_button], spacing=10),
            ft.Container(
                ft.Column([
                    ft.Text("Canciones Individuales", color="white", size=16, weight=ft.FontWeight.BOLD),
                    ft.ListView([uploaded_table], height=150, auto_scroll=True),
                ]),
                margin=ft.margin.only(bottom=20),
            ),
            ft.Row([play_button, pause_button, stop_button], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(progress_slider, margin=ft.margin.only(left=20, right=20, top=20)),
            ft.Container(progress_text, alignment=ft.alignment.center, margin=ft.margin.only(top=10)),
            ft.Container(status_text, alignment=ft.alignment.center, margin=ft.margin.only(top=20)),
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER)
    )

    def copy_song_path(path):
        pyperclip.copy(path)

    def get_song_duration(file_path):
        audio = MP3(file_path)
        return int(audio.info.length)

    def format_time(seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02}:{seconds:02}"

ft.app(target=main)
