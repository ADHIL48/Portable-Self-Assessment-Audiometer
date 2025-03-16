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
        self.data = []
        self.detected = False
        self.previous_results = None

    def player(self, p, repeat=1):
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
                print(f"Playing frequency: {freq} Hz at volume: {vol} dB")
                self.signal = [freq, vol, datetime.now()]
                audio_data = (np.sin(2 * np.pi * np.arange(44100 * 0.5) * freq / 44100)).astype(np.float32)
                audio_data *= 10**(vol / 20)  # Convert dB to amplitude
                stream.write(audio_data.tobytes())
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

        # Save data
        df.to_csv(f'./results_{now:%Y%m%d%H%M%S}_data.csv', index=None)

        # Visualize results
        fig, ax = plt.subplots(1)
        ax.plot(df['frequency'], df['volume'], marker='x')
        ax.set(title=f"Hearing capacity", xlim=[100, 2100], ylim=[0, 90], xticks=[125, 250, 500, 1000, 2000], yticks=[0, 20, 40, 60, 80], xlabel='Frequency (Hz)', ylabel='Volume (dB)')
        ax.grid()
        plt.savefig(f'./results_{now:%Y%m%d%H%M%S}_capacity.png')
        plt.show()  # Display the plot in a separate window
        plt.clf()
        plt.close()

        # Visualize reaction time
        fig, ax = plt.subplots(1)
        ax.plot(df['frequency'], df['reaction_time'], marker='x')
        ax.set(title=f"Reaction time", xlim=[100, 2100], xlabel='Frequency (Hz)', ylabel='ms')
        ax.grid()
        plt.savefig(f'./results_{now:%Y%m%d%H%M%S}_reaction.png')
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
        # Start player with repeat argument
        self.player(p, repeat=args.repeat)  # Pass repeat argument from command line

        # Play greeting
        self.greeting(p, opening=False)

        self.analyse_results()
        print('Test is finished. Please check visualizations.')

if __name__ == '__main__':
    test = HearingTest()
    test.run_test()
