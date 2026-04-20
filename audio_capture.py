import sounddevice as sd
import numpy as np
import queue
import sys

class SystemAudioCapture:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.q = queue.Queue()
        self.stream = None
        self.is_recording = False

    def _callback(self, indata, frames, time, status):
        mono_data = np.mean(indata, axis=1) if indata.shape[1] > 1 else indata[:, 0]
        self.q.put(mono_data.copy())

    def start(self):
        self.is_recording = True
        self.q.queue.clear()

        device_id = None
        extra_settings = None
        channels = 1

        if sys.platform == 'win32':
            try:
                wasapi_info = sd.query_hostapis(sd.find_hostapi('WASAPI'))
                device_id = wasapi_info['default_output_device']
                extra_settings = sd.WasapiSettings(loopback=True)
                device_info = sd.query_devices(device_id)
                channels = device_info['max_input_channels'] or 2
            except Exception as e:
                print(f"Advertencia con WASAPI: {e}")

        self.stream = sd.InputStream(
            device=device_id,
            samplerate=self.sample_rate,
            channels=channels,
            dtype='float32',
            callback=self._callback,
            extra_settings=extra_settings
        )
        self.stream.start()

    def stop(self):
        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()

    def get_chunk(self, duration=3.0):
        frames_needed = int(self.sample_rate * duration)
        frames = []
        frames_gathered = 0

        while frames_gathered < frames_needed and self.is_recording:
            try:
                data = self.q.get(timeout=0.5)
                frames.append(data)
                frames_gathered += len(data)
            except queue.Empty:
                continue

        if not frames:
            return np.array([], dtype=np.float32)

        chunk = np.concatenate(frames, axis=0)
        return chunk
