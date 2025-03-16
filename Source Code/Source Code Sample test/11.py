import argparse
from datetime import datetime
from time import sleep
import numpy as np
import pyaudio
import threading
import pandas as pd
import matplotlib.pyplot as plt
from pyfiglet import Figlet

# Use interactive backend for displaying plots in a separate window
plt.switch_backend('TkAgg')  # You may need to install TkAgg backend if not already installed

class HearingTest:
    def _init_(self):
        self.signal = None
        self.left_data = []
        self.right_data = []
        self.detected = False
        self.previous_results = None

    def player(self, p, repeat=1, ear='both'):
        """Plays sounds with different frequencies and volume levels"""
        volumes = [0, 20, 40, 60, 80]  # Adjusted volume levels in dB
        frequencies = [125, 250, 500, 1000, 2000]  # Adjusted frequencies in Hz

        # Repeat each frequency based on the provided argument
        frequencies = np.repeat(frequencies, repeat)

        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=44100,
                        output=True)

        sleep(0.1)
        for freq in frequencies:
            self.detected = False
            for vol in volumes:
                print(f"Playing frequency: {freq} Hz at volume: {vol} dB for {ear} ear")
                self.signal = [freq, vol, datetime.now()]
                audio_data = (np.sin(2 * np.pi * np.arange(44100 * 0.5) * freq / 44100)).astype(np.float32)
                if ear == 'both' or ear == 'left':
                    audio_data_left = audio_data * 10**(vol / 20)
                if ear == 'both' or ear == 'right':
                    audio_data_right = audio_data * 10**(vol / 20)
                if ear == 'both':
                    stream.write(audio_data_left.tobytes())
                    stream.write(audio_data_right.tobytes())
                elif ear == 'left':
                    stream.write(audio_data_left.tobytes())
                elif ear == 'right':
                    stream.write(audio_data_right.tobytes())
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
                if d[0] == 125:  # Assuming 125 Hz is played first
                    self.left_data.append(d)
                else:
                    self.right_data.append(d)
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

        # Create separate plots for left and right ears
        fig, ax = plt.subplots(2, 1, figsize=(8, 10))

        # Plot left ear data
        left_df = pd.DataFrame(self.left_data, columns=['frequency', 'volume', 'played', 'heard'])
        left_df['reaction_time'] = (left_df['heard'] - left_df['played']).dt.microseconds // 1000
        ax[0].plot(left_df['frequency'], left_df['volume'], marker='x', label='Left Ear')
        ax[1].plot(left_df['frequency'], left_df['reaction_time'], marker='x', label='Left Ear')

        # Plot right ear data
        right_df = pd.DataFrame(self.right_data, columns=['frequency', 'volume', 'played', 'heard'])
        right_df['reaction_time'] = (right_df['heard'] - right_df['played']).dt.microseconds // 1000
        ax[0].plot(right_df['frequency'], right_df['volume'], marker='o', label='Right Ear')
        ax[1].plot(right_df['frequency'], right_df['reaction_time'], marker='o', label='Right Ear')

        # Customize plot
        ax[0].set(title=f"Hearing capacity", xlim=[100, 2100], ylim=[0, 90], xticks=[125, 250, 500, 1000, 2000], yticks=[0, 20, 40, 60, 80], xlabel='Frequency (Hz)', ylabel='Volume (dB)')
        ax[0].grid()
        ax[0].legend()

        ax[1].set(title=f"Reaction time", xlim=[100, 2100], xlabel='Frequency (Hz)', ylabel='ms')
        ax[1].grid()
        ax[1].legend()

        # Save and display plot
        plt.tight_layout()
        plt.savefig(f'./results_{now:%Y%m%d%H%M%S}_combined.png')
        plt.show()
        plt.close()

        # Combine left and right ear data
        left_df['ear'] = 'left'
        right_df['ear'] = 'right'
        df = pd.concat([left_df, right_df])

        return df

    def run_test(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-r', '--repeat', help='Number of times each frequency is repeated', type=int, default=1)  # Change default value to 1
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

        # Run test for both ears
        print('Testing both ears...')
        self.player(p, repeat=args.repeat, ear='both')

        # Analyse and visualize results
        self.analyse_results()
        print('Test is finished. Please check visualizations.')

if _name_ == '_main_':
    test = HearingTest()
    test.run_test()