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
        self.data_left = []
        self.data_right = []
        self.detected = False
        self.previous_results = None

    def player(self, p, ear, repeat=1):
        """Plays sounds with different frequencies and volume levels for specified ear"""
        volumes = [0, 10, 20, 30, 40, 50]  # Adjusted volume levels in dB
        frequencies = [250, 500, 1000, 2000, 4000, 8000]  # Adjusted frequencies in Hz

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
                audio_data = (np.sin(2 * np.pi * np.arange(44100 * 0.5) * freq / 44100)).astype(np.float32)
                audio_data *= 10**(vol / 20)  # Convert dB to amplitude
                stream.write(audio_data.tobytes())
                if self.detected:
                    break
            sleep(2)

        stream.stop_stream()
        stream.close()

    def listener(self, ear):
        """Listens to user input for specified ear"""
        while True:
            r = input()
            d = [datetime.now(), ear]
            print(f'Recording event: {d}')
            if ear == 'left':
                self.data_left.append(d)
            elif ear == 'right':
                self.data_right.append(d)
            self.detected = True

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
        print('* Hit [ENTER] when you start hearing pulsing sound for left ear.  *')
        print('*' * 67)

        p = pyaudio.PyAudio()
        # Left ear test
        print('Left ear test will start in 5 seconds...')
        sleep(5)
        # Start left ear listener
        p2_left = threading.Thread(target=self.listener, args=('left',), daemon=True)
        p2_left.start()
        # Start left ear player with repeat argument
        self.player(p, 'left', repeat=args.repeat)  # Pass repeat argument from command line

        print('*' * 67)
        print('* Please put on your headphones.                                  *')
        print('* Hit [ENTER] when you start hearing pulsing sound for right ear. *')
        print('*' * 67)

        # Right ear test
        print('Right ear test will start in 5 seconds...')
        sleep(5)
        # Start right ear listener
        p2_right = threading.Thread(target=self.listener, args=('right',), daemon=True)
        p2_right.start()
        # Start right ear player with repeat argument
        self.player(p, 'right', repeat=args.repeat)  # Pass repeat argument from command line

        p.terminate()

        self.analyse_results('left')
        self.analyse_results('right')

        print('Test is finished. Please check visualizations for both ears.')

    def analyse_results(self, ear):
        """Stores and visualizes results for specified ear"""
        now = datetime.now()
        data = self.data_left if ear == 'left' else self.data_right

        # Load data to DataFrame
        df = pd.DataFrame(data, columns=['heard', 'ear'])
        df['reaction_time'] = (df['heard'] - df['heard'].shift()).dt.microseconds // 1000

        # Save data
        df.to_csv(f'./results_{ear}_{now:%Y%m%d%H%M%S}_data.csv', index=None)

        # Visualize results
        fig, ax = plt.subplots(1)
        ax.plot(df.index, df['reaction_time'], marker='x')
        ax.set(title=f"Reaction time - {ear.capitalize()} Ear", xlabel='Event', ylabel='Time (ms)')
        ax.grid()
        plt.savefig(f'./results_{ear}_{now:%Y%m%d%H%M%S}_reaction_time.png')
        plt.show()  # Display the plot in a separate window
        plt.clf()
        plt.close()

if __name__ == '__main__':
    test = HearingTest()
    test.run_test()
