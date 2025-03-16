import argparse
from datetime import datetime
from time import sleep
from pysine import sine
import pyaudio
import threading
from pyfiglet import Figlet
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pygame
import os

class HearingTest:
    def __init__(self):
        self.signal = None
        self.data = []
        self.detected = False
        self.previous_results = None

    def player(self, p, repeat=1):
        """Plays sounds with different frequencies and volume levels"""
        volumes = [10, 20, 30, 40, 50]
        frequencies = [125, 250, 500, 1000, 2000, 4000, 8000]  # Adjusted order

        # Shuffle frequencies
        frequencies = np.repeat(frequencies, repeat)
        np.random.shuffle(frequencies)

        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=44100,
                        output=True)

        sleep(0.1)
        for freq in frequencies:
            self.detected = False
            for vol in volumes:
                print(freq, vol)
                for n in range(3):
                    self.signal = [freq, vol, datetime.now()]
                    audio_data = (np.sin(2 * np.pi * np.arange(44100 * 0.5) * freq / 44100)).astype(np.float32)
                    audio_data *= vol / 50.0  # Scale the audio data to adjust volume
                    stream.write(audio_data.tobytes())
                    if self.detected:
                        break
                if self.detected:
                    break
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

    def greeting(self, p, opening=True):
        """Plays simple greeting to check sound"""
        frequencies = [261, 329, 391]
        durations = [0.2, 0.2, 0.5]
        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=44100,
                        output=True)
        sleep(0.1)
        if opening:
            for freq, duration in zip(frequencies, durations):
                audio_data = (np.sin(2 * np.pi * np.arange(int(44100 * duration)) * freq / 44100)).astype(np.float32)
                stream.write((audio_data * 0.5).tobytes())
        else:
            for freq, duration in zip(frequencies[::-1], durations):
                audio_data = (np.sin(2 * np.pi * np.arange(int(44100 * duration)) * freq / 44100)).astype(np.float32)
                stream.write((audio_data * 0.5).tobytes())

        stream.stop_stream()
        stream.close()

    def analyse_results(self):
        """Stores and visualizes results"""
        now = datetime.now()

        # Load data to DataFrame
        df = pd.DataFrame(self.data, columns=['frequency', 'volume', 'played', 'heard'])
        df['reaction_time'] = (df['heard'] - df['played']).dt.microseconds // 1000

        # Average multiple results
        df = df.groupby(['frequency']).mean().reset_index()

        # Save data
        df.to_csv(f'./results_{now:%Y%m%d%H%M%S}_data.csv', index=None)

        # Visualize results
        plt.plot(df['frequency'], df['volume'], marker='x')
        plt.title(f"Hearing capacity")
        plt.ylim([10, 50])
        plt.yticks([10, 20, 30, 40, 50])
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Volume (dB)')
        plt.grid()

        plt.savefig(f'./results_{now:%Y%m%d%H%M%S}_capacity.png')
        plt.close()

        # Visualize reaction time
        plt.plot(df['frequency'], df['reaction_time'], marker='x')
        plt.title(f"Reaction time")
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('ms')
        plt.grid()

        plt.savefig(f'./results_{now:%Y%m%d%H%M%S}_reaction.png')
        plt.close()

        return df

    def run_test(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-r', '--repeat', help='Number of times each frequency is repeated', required=False, default=1)  # Change default value to 1
        args = parser.parse_args()

        f = Figlet(font='slant')
        print(f.renderText('HEARING TEST'))

        print('*' * 67)
        print('* Welcome to Hearing Test                                         *')
        print('*                                                                 *')
        print('* Please put on your headphones.                                  *')
        print('* Hit [ENTER] when you start hearing pulsing sound.               *')
        print('*' * 67)

        p = pyaudio.PyAudio()
        # Play greeting
        self.greeting(p, opening=True)

        print('Test will start in 5 seconds...')
        sleep(5)
        # Start listener
        p2 = threading.Thread(target=self.listener, daemon=True)
        p2.start()
        # Start player with repeat=1
        self.player(p, repeat=1)  # Change repeat to 1

        # Play greeting
        self.greeting(p, opening=False)

        # Initialize Pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Hearing Test Visualization")

        # Load and display capacity graph
        capacity_image = pygame.image.load(f'./results_{datetime.now():%Y%m%d%H%M%S}_capacity.png')
        screen.blit(capacity_image, (0, 0))
        pygame.display.flip()

        # Load and display reaction time graph
        reaction_image = pygame.image.load(f'./results_{datetime.now():%Y%m%d%H%M%S}_reaction.png')
        screen.blit(reaction_image, (0, 300))
        pygame.display.flip()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        pygame.quit()

        print('Test is finished. Please check visualizations.')


if __name__ == '__main__':
    test = HearingTest()
    test.run_test()
