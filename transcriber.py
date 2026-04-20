from faster_whisper import WhisperModel
import numpy as np

class AudioTranscriber:
    def __init__(self):
        self.model = None

    def load_model(self):
        if self.model is None:
            self.model = WhisperModel("base", device="cpu", compute_type="int8")

    def transcribe(self, audio_chunk: np.ndarray, language: str) -> str:
        if len(audio_chunk) == 0:
            return ""

        lang_code = "es" if language == "Español" else "en"

        segments, _ = self.model.transcribe(
            audio_chunk, 
            language=lang_code,
            beam_size=5,
            vad_filter=True
        )

        text = " ".join([segment.text for segment in segments])
        return text.strip()
