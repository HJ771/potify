import flet as ft
import pygame
import os
from pathlib import Path

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

    upload_button = ft.ElevatedButton("Subir Música", icon=ft.icons.UPLOAD_FILE, on_click=lambda _: file_picker.pick_files(allow_multiple=True))
    folder_button = ft.ElevatedButton("Subir Carpeta", icon=ft.icons.FOLDER_OPEN, on_click=lambda _: folder_picker.get_directory_path())

    page.add(
        ft.Column([
            title,
            ft.Row([upload_button, folder_button], alignment=ft.MainAxisAlignment.CENTER),
            ft.Text("Canciones Individuales", color="white", size=16, weight=ft.FontWeight.BOLD),
            uploaded_table,
            ft.Text("Playlist", color="white", size=16, weight=ft.FontWeight.BOLD),
            playlist_table,
        ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
    )

ft.app(target=main)
