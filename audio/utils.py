import numpy as np
import pyaudio
import threading

class AudioThread(threading.Thread):
    def __init__(self, buffer_size=1024, fs=44100):
        threading.Thread.__init__(self)
        self.buffer_size = buffer_size
        self.fs = fs
        self.current_volume = 0.3
        self.current_freq = 440  # Start with A4 note
        self.is_sound_on = False
        self.target_freq = self.current_freq
        self.target_volume = self.current_volume
        self.phase = 0
        self.running = True

    def run(self):
        alpha_freq = 0.15
        alpha_volume = 0.15

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32,
                            channels=1,
                            rate=self.fs,
                            output=True,
                            frames_per_buffer=self.buffer_size)

        while self.running:
            if self.is_sound_on:
                self.current_freq = self.current_freq * (1 - alpha_freq) + self.target_freq * alpha_freq
                self.current_volume = self.current_volume * (1 - alpha_volume) + self.target_volume * alpha_volume

                samples, self.phase = self.generate_sine_wave(self.current_freq, self.buffer_size, self.phase)
                output_samples = samples * self.current_volume
            else:
                samples, self.phase = self.generate_sine_wave(self.current_freq, self.buffer_size, self.phase)
                output_samples = samples * self.current_volume * max(0, 1 - self.phase / (0.1 * self.fs))
                if self.phase > 0.1 * self.fs:
                    output_samples = np.zeros(self.buffer_size)
                    self.phase = 0
            self.stream.write(output_samples.astype(np.float32).tobytes())

    def generate_sine_wave(self, freq, num_samples, start_phase):
        t = np.linspace(0, num_samples / self.fs, num_samples, False)
        phase = (start_phase + 2 * np.pi * freq * t) % (2 * np.pi)
        wave = np.sin(phase)
        return wave, phase[-1]

    def stop(self):
        self.running = False

# Define note frequencies (C4 to C5)
note_frequencies = {
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
    'G4': 392.00, 'A4': 440.00, 'B4': 493.88, 'C5': 523.25
}