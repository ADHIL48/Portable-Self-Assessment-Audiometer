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
    def __init__(self):
        self.signal = None
        self.left_data = []
        self.right_data = []
        self.detected = False
        self.previous_results = None

    def player(self, p, repeat=1, ear='both'):
        """Plays sounds with different frequencies and volume levels"""
        volumes = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]  # Adjusted volume levels in dB
        frequencies = [125, 250, 500, 1000, 2000, 4000, 8000]  # Adjusted frequencies in Hz

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

    def analyse_results(self, data, ear):
        """Stores and visualizes results"""
        now = datetime.now()

        # Load data to DataFrame
        df = pd.DataFrame(data, columns=['frequency', 'volume', 'played', 'heard'])
        df['reaction_time'] = (df['heard'] - df['played']).dt.microseconds // 1000

        # Save data
        df.to_csv(f'./results_{ear}_{now:%Y%m%d%H%M%S}_data.csv', index=None)

        # Visualize results
        fig, ax = plt.subplots(1)
        ax.plot(df['frequency'], df['volume'], marker='x', label=ear)
        ax.set(title=f"Hearing capacity for {ear} ear", xlim=[100, 9000], ylim=[0, 90], xticks=[125, 250, 500, 1000, 2000, 4000, 8000], yticks=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90], xlabel='Frequency (Hz)', ylabel='Volume (dB)')
        ax.grid()
        ax.legend()
        plt.savefig(f'./results_{ear}_{now:%Y%m%d%H%M%S}_capacity.png')
        plt.show()  # Display the plot in a separate window
        plt.clf()
        plt.close()

        # Visualize reaction time
        fig, ax = plt.subplots(1)
        ax.plot(df['frequency'], df['reaction_time'], marker='x', label=ear)
        ax.set(title=f"Reaction time for {ear} ear", xlim=[100, 9000], xlabel='Frequency (Hz)', ylabel='ms')
        ax.grid()
        ax.legend()
        plt.savefig(f'./results_{ear}_{now:%Y%m%d%H%M%S}_reaction.png')
        plt.show()  # Display the plot in a separate window
        plt.clf()
        plt.close()

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

        # Run test for the left ear
        print('Testing left ear...')
        self.player(p, repeat=args.repeat, ear='left')

        # Analyse and visualize results for the left ear
        left_df = self.analyse_results(self.left_data, 'left')

        # Reset data for the next test
        self.left_data = []

        # Play greeting
        self.greeting(p, opening=False)

        # Run test for the right ear
        print('Testing right ear...')
        self.player(p, repeat=args.repeat, ear='right')

        # Analyse and visualize results for the right ear
        right_df = self.analyse_results(self.right_data, 'right')
        self.right_data = []

        print('Test is finished. Please check visualizations.')

if __name__ == '__main__':
    test = HearingTest()
    test.run_test()
