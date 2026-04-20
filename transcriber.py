from faster_whisper import WhisperModel
import numpy as np

class AudioTranscriber:
    def __init__(self):
        self.model = None
        self.previous_text = ""

    def load_model(self):
        if self.model is None:
            self.model = WhisperModel("base", device="cpu", compute_type="int8")

    def transcribe(self, audio_chunk: np.ndarray, language: str) -> str:
        if len(audio_chunk) == 0:
            return ""

        lang_code = "es" if language == "Español" else "en"

        audio_chunk = audio_chunk / max(1e-6, np.max(np.abs(audio_chunk)))
        audio_chunk = np.clip(audio_chunk, -1.0, 1.0)

        segments, _ = self.model.transcribe(
            audio_chunk, 
            language=lang_code,
            beam_size=5,
            best_of=5,
            temperature=0.0,
            condition_on_previous_text=True,
            initial_prompt=self.previous_text,
            vad_filter=True
        )

        text = " ".join([segment.text for segment in segments]).strip()

        if text:
            self.previous_text += " " + text
            self.previous_text = self.previous_text[-200:]

        return text
