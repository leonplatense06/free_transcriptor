import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import threading
import os

from audio_capture import SystemAudioCapture
from transcriber import AudioTranscriber

BG_COLOR = "#F4F1DE"
BTN_IDLE = "#81B29A"
BTN_IDLE_HOVER = "#5B8E7D"
BTN_REC = "#FF3B30"
BTN_REC_HOVER = "#D32F2F"
TEXT_BG = "#FFFFFF"
TEXT_FG = "#3D405B"

FONT_UI = ("Segoe UI", 15, "normal")
FONT_TEXT = ("Segoe UI", 14, "normal")
FONT_REC = ("Segoe UI", 24, "bold")

class CozyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Transcriptor Cozy")
        self.geometry("400x560")
        self.configure(fg_color=BG_COLOR)
        self.resizable(False, True)

        icon_path = os.path.join(os.path.dirname(__file__), "ranita.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        self.audio_capture = SystemAudioCapture()
        self.transcriber = AudioTranscriber()
        self.is_running = False
        self.transcription_thread = None

        self._build_ui()

    def _build_ui(self):
        png_path = os.path.join(os.path.dirname(__file__), "ranita.png")
        if os.path.exists(png_path):
            img = ctk.CTkImage(Image.open(png_path), size=(80, 80))
            self.logo_label = ctk.CTkLabel(self, image=img, text="")
        else:
            self.logo_label = ctk.CTkLabel(self, text="🐸", font=("Segoe UI", 50), text_color=BTN_IDLE)
        self.logo_label.pack(pady=(15, 5))

        self.lang_var = ctk.StringVar(value="Español")
        self.lang_menu = ctk.CTkOptionMenu(
            self, 
            variable=self.lang_var, 
            values=["Español", "Inglés"],
            fg_color=BTN_IDLE,
            button_color=BTN_IDLE_HOVER,
            button_hover_color=BTN_IDLE_HOVER,
            font=FONT_UI,
            dropdown_font=FONT_UI
        )
        self.lang_menu.pack(pady=10)

        self.textbox = ctk.CTkTextbox(
            self, 
            width=360, 
            height=200, 
            fg_color=TEXT_BG, 
            text_color=TEXT_FG,
            corner_radius=10,
            font=FONT_TEXT
        )
        self.textbox.pack(pady=10, padx=20, fill="both", expand=True)
        self.textbox.configure(state="disabled")

        self.status_label = ctk.CTkLabel(self, text="Esperando...", text_color=TEXT_FG, font=("Segoe UI", 12, "italic"))
        self.status_label.pack(pady=(0, 5))

        self.btn_toggle = ctk.CTkButton(
            self, 
            text="●", 
            width=70,
            height=70,
            corner_radius=35,
            command=self.toggle_transcription,
            fg_color=BTN_IDLE,
            hover_color=BTN_IDLE_HOVER,
            font=FONT_REC
        )
        self.btn_toggle.pack(pady=5)

        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(pady=15)

        self.btn_copy = ctk.CTkButton(
            self.bottom_frame, text="Copiar", command=self.copy_to_clipboard, width=100,
            fg_color="#E07A5F", hover_color="#C0604A", font=FONT_UI
        )
        self.btn_copy.pack(side="left", padx=10)

        self.btn_export = ctk.CTkButton(
            self.bottom_frame, text="Exportar", command=self.export_to_txt, width=100,
            fg_color="#F2CC8F", hover_color="#D8B273", text_color="#3D405B", font=FONT_UI
        )
        self.btn_export.pack(side="left", padx=10)

    def toggle_transcription(self):
        if not self.is_running:
            self.is_running = True
            self.btn_toggle.configure(fg_color=BTN_REC, hover_color=BTN_REC_HOVER)
            self.lang_menu.configure(state="disabled")
            self.transcriber.previous_text = ""

            self.textbox.configure(state="normal")
            self.textbox.delete("1.0", "end")
            self.textbox.configure(state="disabled")

            self.transcription_thread = threading.Thread(target=self._transcription_loop, daemon=True)
            self.transcription_thread.start()
        else:
            self.is_running = False
            self.btn_toggle.configure(fg_color=BTN_IDLE, hover_color=BTN_IDLE_HOVER)
            self.lang_menu.configure(state="normal")
            self.audio_capture.stop()

    def _transcription_loop(self):
        self.transcriber.load_model()
        self.audio_capture.start()
        language = self.lang_var.get()

        while self.is_running:
            chunk = self.audio_capture.get_chunk(duration=6.0)
            if not self.is_running:
                break
            if len(chunk) > 0:
                text = self.transcriber.transcribe(chunk, language)
                if text:
                    self.after(0, self._append_text, text)

    def _append_text(self, text):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", text + " ")
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def copy_to_clipboard(self):
        texto = self.textbox.get("1.0", "end").strip()
        if texto:
            self.clipboard_clear()
            self.clipboard_append(texto)
            self.update()

    def export_to_txt(self):
        texto = self.textbox.get("1.0", "end").strip()
        if not texto:
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")]
        )
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(texto)
