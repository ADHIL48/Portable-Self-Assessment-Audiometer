import argparse
from datetime import datetime
from time import sleep
import numpy as np
import pyaudio

class HearingTest:
    def __init__(self):
        self.signal = None
        self.data = []
        self.detected = False
        self.previous_results = None

    def player(self, p):
        """Plays sounds with different frequencies and volume levels"""
        frequencies = [125, 250, 500, 1000, 2000]
        volumes = [0, 20, 40, 60, 80]

        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=44100,
                        output=True)

        sleep(0.1)
        for freq, vol in zip(frequencies, volumes):
            self.detected = False
            print(f'Playing frequency: {freq} Hz at volume: {vol} dB')
            self.signal = [freq, vol, datetime.now()]
            audio_data = (np.sin(2 * np.pi * np.arange(44100 * 0.5) * freq / 44100)).astype(np.float32)
            audio_data *= 10**(vol / 20)  # Convert dB to amplitude
            stream.write(audio_data.tobytes())
            sleep(2)

        stream.stop_stream()
        stream.close()

    def listener(self):
        """Listens to user input"""
        while True:
            r = input()
            if self.signal:
                d = self.signal + [datetime.now()]
                print(f'Recording event: {d}')
                self.data.append(d)
                self.detected = True

    def run_test(self):
        parser = argparse.ArgumentParser()
        args = parser.parse_args()

        # Initialize PyAudio
        p = pyaudio.PyAudio()

        # Play frequencies
        self.player(p)

        # Close PyAudio
        p.terminate()

if __name__ == '__main__':
    test = HearingTest()
    test.run_test()
