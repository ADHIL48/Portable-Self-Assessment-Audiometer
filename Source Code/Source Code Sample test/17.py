import argparse
from datetime import datetime
from time import sleep
import numpy as np
import pyaudio
import threading
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class HearingTest:
    def __init__(self):
        self.signal = None
        self.right_data = []
        self.detected = False

    def player(self, p, repeat=1, ear='right'):
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
                if ear == 'right':
                    audio_data_right = audio_data * 10**(vol / 20)
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
                self.right_data.append(d)
                self.detected = True

    def analyse_results(self, data, ear):
        """Stores and visualizes results"""
        now = datetime.now()

        # Load data to DataFrame
        df = pd.DataFrame(data, columns=['frequency', 'volume', 'played', 'heard'])
        df['reaction_time'] = (df['heard'] - df['played']).dt.microseconds // 1000

        # Save data
        df.to_csv(f'./results_{ear}_{now:%Y%m%d%H%M%S}_data.csv', index=None)

        # Plotting audiogram
        thresholds = {
            'Normal': 15,
            'Slight': 25,
            'Mild': 40,
            'Moderate': 55,
            'Moderately Severe': 70,
            'Severe': 90,
            'Profound': np.inf
        }

        # Define colors for different stages of hearing loss
        colors = {
            'Normal': 'green',
            'Slight': 'yellow',
            'Mild': 'orange',
            'Moderate': 'red',
            'Moderately Severe': 'purple',
            'Severe': 'brown',
            'Profound': 'black'
        }

        # Create a new Tkinter window
        root = tk.Tk()
        root.title(f'Audiogram - {ear.capitalize()} Ear')

        # Create a matplotlib figure
        fig, ax = plt.subplots(figsize=(8, 6))

        # Plotting audiogram with colored rows
        for stage, threshold in thresholds.items():
            # Filter frequencies based on threshold
            filtered_indices = df['volume'][df['volume'] >= threshold].index
            if len(filtered_indices) > 0:
                stage_frequencies = df['frequency'].iloc[filtered_indices]
                # Plot scatter points
                ax.scatter(stage_frequencies, [threshold] * len(stage_frequencies), marker='o', color=colors[stage], label=stage)

        # Plotting the audiogram
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Volume (dB)')
        ax.grid(True)
        ax.legend()

        # Embed the matplotlib figure into the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Run the Tkinter event loop
        tk.mainloop()

        return df

    def run_test(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-r', '--repeat', help='Number of times each frequency is repeated', type=int, default=1)  # Change default value to 1
        args = parser.parse_args()

        print('*' * 67)
        print('* Welcome to Hearing Test                                         *')
        print('*                                                                 *')
        print('* Please put on your headphones.                                  *')
        print('* Hit [ENTER] when you start hearing pulsing sound.               *')
        print('*' * 67)

        print('Test will start in 5 seconds...')
        sleep(5)
        # Start listener
        p2 = threading.Thread(target=self.listener, daemon=True)
        p2.start()

        # Run test for the right ear
        print('Testing right ear...')
        p = pyaudio.PyAudio()
        self.player(p, repeat=args.repeat, ear='right')

        # Analyse and visualize results for the right ear
        right_df = self.analyse_results(self.right_data, 'right')
        self.right_data = []

        print('Test is finished. Please check visualizations.')

if __name__ == '__main__':
    test = HearingTest()
    test.run_test()
