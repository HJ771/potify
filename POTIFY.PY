import flet as ft
import pygame
from pathlib import Path
from mutagen.mp3 import MP3
import asyncio
import os

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
            ft.DataColumn(ft.Text("Acción", color="white")),
        ],
        rows=[],
        bgcolor="#1E1E1E",
        border=ft.border.all(1, "#BB86FC"),
        column_spacing=20,
    )

    playlist_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nombre del Archivo", color="white")),
            ft.DataColumn(ft.Text("Acción", color="white")),
        ],
        rows=[],
        bgcolor="#1E1E1E",
        border=ft.border.all(1, "#BB86FC"),
        column_spacing=20,
    )

    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            uploaded_table.rows.clear()
            for index, file in enumerate(e.files):
                uploaded_songs.append(file.path)
                uploaded_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(Path(file.path).name, color="white")),
                            ft.DataCell(
                                ft.IconButton(
                                    icon=ft.icons.PLAY_ARROW,
                                    on_click=lambda _, idx=index: play_song(idx, uploaded_songs),
                                )
                            ),
                        ]
                    )
                )
            page.update()

    def pick_folder_result(e: ft.FilePickerResultEvent):
        if e.path:
            playlist_table.rows.clear()
            folder_path = e.path
            for index, file in enumerate(os.listdir(folder_path)):
                if file.endswith(".mp3"):
                    full_path = os.path.join(folder_path, file)
                    playlist_songs.append(full_path)
                    playlist_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(file, color="white")),
                                ft.DataCell(
                                    ft.IconButton(
                                        icon=ft.icons.PLAY_ARROW,
                                        on_click=lambda _, idx=index: play_song(idx, playlist_songs),
                                    )
                                ),
                            ]
                        )
                    )
            page.update()

    file_picker = ft.FilePicker(on_result=pick_files_result)
    folder_picker = ft.FilePicker(on_result=pick_folder_result)
    page.overlay.extend([file_picker, folder_picker])

    progress_slider = ft.Slider(min=0, max=100, value=0, disabled=True)
    progress_text = ft.Text("00:00 / 00:00", color="white", size=12)

    def get_song_duration(file_path):
        try:
            audio = MP3(file_path)
            return int(audio.info.length)
        except Exception as e:
            print(f"Error al obtener la duración de la canción: {e}")
            return 0

    def play_song(index, song_list):
        nonlocal current_song_index, song_duration, is_playing
        if 0 <= index < len(song_list):
            current_song_index = index
            pygame.mixer.music.load(song_list[index])
            song_duration = get_song_duration(song_list[index])
            if song_duration == 0:
                print("No se pudo obtener la duración de la canción.")
                return
            progress_slider.max = song_duration
            progress_slider.value = 0
            pygame.mixer.music.play()
            is_playing = True
            page.run_task(update_progress)
            status_text.value = f"Reproduciendo: {Path(song_list[index]).name}"
            page.update()

    def toggle_pause(e):
        global is_playing
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            is_playing = False
            status_text.value = "Pausado"
        else:
            pygame.mixer.music.unpause()
            is_playing = True
            status_text.value = f"Reproduciendo: {Path(uploaded_songs[current_song_index]).name}"
        page.update()

    def stop_song(e):
        global is_playing
        pygame.mixer.music.stop()
        is_playing = False
        progress_slider.value = 0
        progress_text.value = "00:00 / 00:00"
        status_text.value = "Detenido"
        page.update()

    async def update_progress():
        while is_playing and current_song_index is not None:
            try:
                position = pygame.mixer.music.get_pos() / 1000
                if position >= song_duration:
                    stop_song(None)
                    break
                progress_slider.value = position
                progress_text.value = f"{format_time(position)} / {format_time(song_duration)}"
                page.update()
            except Exception as e:
                print(f"Error al actualizar la barra de tiempo: {e}")
            await asyncio.sleep(0.5)

    def format_time(seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02}:{seconds:02}"

    upload_button = ft.ElevatedButton(
        "Subir Música",
        icon=ft.icons.UPLOAD_FILE,
        on_click=lambda _: file_picker.pick_files(allow_multiple=True),
        bgcolor="#BB86FC",
        color="#121212",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    folder_button = ft.ElevatedButton(
        "Subir Carpeta",
        icon=ft.icons.FOLDER_OPEN,
        on_click=lambda _: folder_picker.get_directory_path(),
        bgcolor="#BB86FC",
        color="#121212",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )

    play_button = ft.IconButton(icon=ft.icons.PLAY_ARROW, on_click=lambda _: play_song(current_song_index or 0, uploaded_songs))
    pause_button = ft.IconButton(icon=ft.icons.PAUSE, on_click=toggle_pause)
    stop_button = ft.IconButton(icon=ft.icons.STOP, on_click=stop_song)

    status_text = ft.Text("Sin reproducción", color="white", size=14)

    page.add(
        ft.Column([
            ft.Container(
                content=title,
                alignment=ft.alignment.center,
                margin=ft.margin.only(top=20, bottom=20),
            ),
            ft.Row([
                ft.Container(
                    content=upload_button,
                    expand=True,
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(right=10),
                ),
                ft.Container(
                    content=folder_button,
                    expand=True,
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(left=10),
                ),
            ], spacing=10),
            ft.Container(
                content=ft.Column([
                    ft.Text("Canciones Individuales", color="white", size=16, weight=ft.FontWeight.BOLD),
                    ft.ListView(
                        controls=[uploaded_table],
                        height=150,
                        auto_scroll=True,
                    ),
                ]),
                margin=ft.margin.only(bottom=20),
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("Playlist", color="white", size=16, weight=ft.FontWeight.BOLD),
                    ft.ListView(
                        controls=[playlist_table],
                        height=150,
                        auto_scroll=True,
                    ),
                ]),
                margin=ft.margin.only(bottom=20),
            ),
            ft.Row([play_button, pause_button, stop_button], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(
                content=progress_slider,
                margin=ft.margin.only(left=20, right=20, top=20),
            ),
            ft.Container(
                content=progress_text,
                alignment=ft.alignment.center,
                margin=ft.margin.only(top=10),
            ),
            ft.Container(
                content=status_text,
                alignment=ft.alignment.center,
                margin=ft.margin.only(top=20),
            ),
        ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
    )

ft.app(target=main)



